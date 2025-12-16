import re
import json
from typing import Dict, Any, List, Optional

class OutputEngine:
    """
    Formats raw LLM outputs into structured responses for the frontend.
    Handles Markdown, Charts, Tables, and Citations.
    """

    def format_fundamental_response(self, raw_text: str, rag_docs: List[Dict], market_data: Dict) -> Dict[str, Any]:
        """
        Formats the response from the Fundamental Agent.
        """
        # 0. Fix bare JSON charts (if LLM forgot code block)
        # This now handles JSON anywhere in the text
        raw_text = self._wrap_bare_json_chart(raw_text)

        # 1. Extract Tables (if any in markdown)
        tables = self._extract_tables(raw_text)
        
        # 2. Extract Charts (if time-series data found)
        charts = self._extract_charts(raw_text)
        
        # 3. Verify Citations & Clean Text
        # Extract citations from text: [Source: DocName, Page X]
        # We strip them from the body and append them at the end
        citations = []
        citation_pattern = r"\[Source: (.*?)\]"
        
        # Find all citations
        matches = re.findall(citation_pattern, raw_text)
        for m in matches:
            citations.append(m)
            
        # Remove inline tags from text
        clean_text = re.sub(r"\[Source: .*?\]", "", raw_text).strip()
        
        # Append consolidated Sources section
        if citations:
            unique_citations = sorted(list(set(citations)))
            clean_text += "\n\n### Sources\n"
            for c in unique_citations:
                clean_text += f"- {c}\n"
        
        # ---- SAFETY FENCE: Final check for bare JSON charts ----
        # If we still have bare JSON that looks like a chart, wrap it.
        # We check for "type": and "series": independently to handle whitespace/newlines.
        if '"type":' in clean_text and '"series":' in clean_text:
            if "```json-chart" not in clean_text:
                try:
                    # Attempt to find and wrap the JSON object at the end
                    json_start = clean_text.rfind("{")
                    if json_start != -1:
                        # Simple brace counting to find the end
                        balance = 0
                        json_end = -1
                        for i, char in enumerate(clean_text[json_start:]):
                            if char == '{':
                                balance += 1
                            elif char == '}':
                                balance -= 1
                                if balance == 0:
                                    json_end = json_start + i + 1
                                    break
                        
                        if json_end != -1:
                            candidate = clean_text[json_start:json_end]
                            # Verify it's valid JSON and looks like a chart
                            if '"type"' in candidate and '"series"' in candidate:
                                try:
                                    json.loads(candidate)
                                    # It's valid. Wrap it.
                                    # We append it if it was at the end, or replace it?
                                    # User suggestion: "cleaned_text += fenced"
                                    # But if it's already in the text (bare), we should replace it to avoid duplicates.
                                    # However, user says "cleaner removes almost everything", implying it might be gone?
                                    # But here we found it in `clean_text`.
                                    # Let's replace it to be safe and clean.
                                    fenced = f"\n```json-chart\n{candidate}\n```\n"
                                    clean_text = clean_text[:json_start] + fenced + clean_text[json_end:]
                                    print("✅ [OutputEngine] Safety Fence applied wrapping.")
                                except:
                                    pass
                except Exception as e:
                    print(f"⚠️ [OutputEngine] Safety Fence error: {e}")

        return {
            "markdown": clean_text,
            "tables": tables,
            "charts": charts,
            "citations": citations, # Keep raw list for metadata if needed
            "overlay": {} # No technical overlay for fundamental
        }

    def format_market_response(self, raw_text: str, market_data: Dict) -> Dict[str, Any]:
        """
        Formats the response from the Market Agent.
        """
        # 1. Extract Overlay JSON
        # We look for a JSON block in the text that defines levels/zones
        overlay = self._extract_json_block(raw_text, "overlay")
        
        # 2. Clean Markdown (remove the JSON block from display text)
        clean_text = self._remove_json_block(raw_text, "overlay")
        
        # 3. Fix bare JSON charts (if LLM forgot code block)
        # We do this AFTER removing overlay to avoid confusion
        clean_text = self._wrap_bare_json_chart(clean_text)

        return {
            "markdown": clean_text,
            "tables": [],
            "charts": [], # Market agent usually annotates existing charts
            "citations": [],
            "overlay": overlay
        }

    def _wrap_bare_json_chart(self, text: str) -> str:
        """
        Detects if the text contains bare JSON chart objects OR generic json blocks, 
        and ensures they are wrapped in ```json-chart blocks.
        """
        try:
            # Case 1: Convert generic ```json blocks to ```json-chart if they contain chart data
            # We use a regex to find generic json blocks
            def replace_json_tag(match):
                content = match.group(1)
                if '"type"' in content and '"series"' in content:
                    return f"```json-chart\n{content}\n```"
                return match.group(0)
            
            text = re.sub(r"```json\s*(\{.*?\})\s*```", replace_json_tag, text, flags=re.DOTALL)

            # Case 2: Wrap bare JSON objects
            # Find all occurrences of '{'
            indices = [i for i, char in enumerate(text) if char == '{']
            
            valid_charts = []
            
            # Identify all valid chart objects
            for start in indices:
                snippet = text[start:]
                # Fast fail
                if '"type"' not in snippet or '"series"' not in snippet:
                    continue
                
                # Find matching brace
                balance = 0
                end = -1
                for k, char in enumerate(snippet):
                    if char == '{':
                        balance += 1
                    elif char == '}':
                        balance -= 1
                        if balance == 0:
                            end = start + k + 1
                            break
                
                if end != -1:
                    candidate = text[start:end]
                    # Check if it's already wrapped
                    # Look at 20 chars before
                    pre_context = text[max(0, start-20):start]
                    if "```json-chart" in pre_context or "```json" in pre_context:
                        continue

                    try:
                        json.loads(candidate)
                        print(f"✅ [OutputEngine] Found valid bare JSON chart at index {start}")
                        valid_charts.append((start, end, candidate))
                    except json.JSONDecodeError as e:
                        print(f"⚠️ [OutputEngine] JSON Decode Error at {start}: {e}")
                        continue
            
            # Filter overlaps: if we have nested valid JSONs, keep the outermost?
            # Or just process them. Since we process from back to front, we need to be careful.
            # If we have { A { B } }, and both are valid charts (unlikely), 
            # wrapping B first: { A ```...B...``` } -> A might no longer be valid JSON?
            # Actually, usually charts are disjoint or top-level.
            # Let's sort by start index descending and apply wraps.
            # If a chart is inside another, we might have issues. 
            # But for this use case, charts are usually sequential.
            
            # Sort by start index descending
            valid_charts.sort(key=lambda x: x[0], reverse=True)
            
            result_text = text
            last_wrap_start = float('inf')
            
            for start, end, candidate in valid_charts:
                # Ensure no overlap with previously wrapped chart (which is later in text)
                if end > last_wrap_start:
                    continue
                
                # Wrap it
                # We need to adjust indices? No, because we work from back to front on the original string?
                # Wait, if we modify result_text, indices shift.
                # But we are iterating on `valid_charts` which has indices into `text` (original).
                # So we must construct `result_text` carefully or use string replacement logic that handles shifts.
                # Actually, since we go from back to front, the indices of *earlier* chunks in `text` 
                # correspond correctly to `result_text` if we only modified parts *after* them.
                # Yes, that's why reverse order works.
                
                pre = result_text[:start]
                post = result_text[end:]
                
                # Double check we didn't mess up the "post" part if we already modified it?
                # If we modified `result_text` at index 500, and now we are at 100.
                # `result_text[:100]` is same as `text[:100]`.
                # `result_text[end:]` ... wait. `end` is an index into `text`.
                # If we inserted text at 500, the stuff at 100..end is still at 100..end relative to start?
                # No. `end` is absolute index in `text`.
                # If we inserted stuff later, `result_text` is longer than `text`.
                # So `result_text[end:]` is NOT correct if we use `end` from `text`.
                
                # Correct approach for multiple replacements:
                # 1. Collect all replacements (start, end, replacement_string)
                # 2. Sort by start desc
                # 3. Apply
                
                fenced = f"\n```json-chart\n{candidate}\n```\n"
                
                # We are replacing text[start:end] with fenced.
                # Since we iterate reverse, `start` is valid for `result_text`?
                # No, `result_text` changes.
                # But if we only change things *after* `start`, then `start` is stable?
                # Yes.
                # But `end`? `end` is `start + len`.
                # So we are replacing the block at `start`.
                # If we previously modified something at `start + 1000`, 
                # that modification is in `result_text` but shifted?
                # No, if we modify from back to front:
                # 1. Replace at 1000. `result_text` = text[:1000] + new + text[1005:]
                # 2. Replace at 100. `result_text` = result_text[:100] + new + result_text[105:]
                # Wait, `result_text[:100]` IS `text[:100]`.
                # `result_text[105:]` includes the modification we did at 1000.
                # So yes, this works!
                
                # But we must use `result_text` for the "post" part.
                # And we must know where `end` maps to in `result_text`.
                # Actually, if we are replacing `text[start:end]`, 
                # and we haven't touched anything before `end` (since we sort desc and check overlap),
                # then `text[start:end]` is exactly what we want to replace.
                # BUT `result_text` has changed *after* `end`.
                # So we can't index `result_text` using `end`.
                
                # Better: keep `text` as reference, build parts.
                # Actually, just use string slicing on `result_text`?
                # If we replace at 1000, `result_text` grows.
                # Now we are at 100. `start`=100, `end`=150.
                # The text at 100..150 in `result_text` is SAME as in `text`.
                # So we can just do:
                # result_text = result_text[:start] + fenced + result_text[end:]
                # WAIT. `result_text[end:]`?
                # If `result_text` grew, `result_text[end:]` is WRONG. It skips the growth?
                # No, `result_text` is longer. `end` is an index into `text`.
                # `result_text` has extra stuff.
                # We need `result_text[end + offset:]`?
                
                # Let's simplify.
                # We have a list of (start, end, replacement).
                # We sort by start desc.
                # We build the string.
                
                # current_text = text
                # for start, end, repl in replacements:
                #    current_text = current_text[:start] + repl + current_text[end:]
                # This is correct ONLY IF `current_text[end:]` refers to the *already modified* tail.
                # But `current_text[end:]` uses `end` which is an index into `text` (original).
                # If `current_text` is longer than `text`, `current_text[end:]` cuts off the *start* of the tail?
                # NO! `current_text` is longer. `end` is small.
                # `current_text[end:]` gives us a HUGE tail.
                # It includes the stuff we just added?
                # Example: text="A...B", len=10. Replace B at 8..9 with "BBB".
                # current="A...BBB". len=12.
                # Now replace A at 0..1 with "AAA".
                # current = current[:0] + "AAA" + current[1:].
                # current[1:] is "...BBB".
                # So yes, it works!
                
                last_wrap_start = start
                result_text = result_text[:start] + fenced + result_text[end:]
            
            return result_text
            
        except Exception:
            return text

    def _extract_charts(self, text: str) -> List[Dict]:
        """
        Extracts chart data from json-chart blocks.
        """
        charts = []
        pattern = r"```json-chart\s*(\{.*?\})\s*```"
        
        for match in re.finditer(pattern, text, re.DOTALL):
            try:
                charts.append(json.loads(match.group(1)))
            except:
                continue
        
        return charts

    def _extract_tables(self, text: str) -> List[Dict]:
        """
        Finds Markdown tables and converts them to JSON.
        Placeholder until full parser is added.
        """
        return []

    def _verify_citations(self, text: str, docs: List[Dict]) -> List[str]:
        """
        Extracts [Source: ...] tags and maps them to doc metadata.
        (Legacy helper, logic moved to main format function for stripping)
        """
        citations = []
        matches = re.findall(r'\[Source: (.*?)\]', text)
        for m in matches:
            citations.append(m)
        return list(set(citations))

    def _extract_json_block(self, text: str, key: str) -> Dict:
        """
        Extracts a JSON block. Supports both ```json ... ``` blocks and raw JSON at the end of text.
        """
        try:
            # 1. Try finding markdown block
            pattern = r"```json\s*({.*?})\s*```"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                return data.get(key, data)
            
            # 2. Try finding raw JSON at the end (looking for last brace)
            # We search for the last occurrence of "overlay": { ... } structure
            # This is a bit heuristic but works for the prompt "Append raw JSON at the end"
            json_start = text.rfind("{")
            if json_start != -1:
                potential_json = text[json_start:]
                try:
                    data = json.loads(potential_json)
                    if key in data:
                        return data[key]
                    # If the root object IS the overlay (e.g. {"supply_zones": ...})
                    # we might need to be careful. But our prompt asks for {"overlay": ...}
                    return data.get(key, {})
                except:
                    pass
                    
        except Exception:
            pass
        return {}

    def _remove_json_block(self, text: str, key: str) -> str:
        """
        Removes the JSON block from the text to keep the UI clean.
        """
        # 1. Remove markdown block
        pattern = r"```json\s*({.*?})\s*```"
        text = re.sub(pattern, "", text, flags=re.DOTALL)
        
        # 2. Remove raw JSON at the end if it matches the key
        # We'll just remove the last JSON-like structure if it contains the key
        try:
            json_start = text.rfind("{")
            if json_start != -1:
                potential_json = text[json_start:]
                if f'"{key}"' in potential_json:
                    text = text[:json_start]
        except:
            pass
            
        return text.strip()

# Singleton instance
output_engine = OutputEngine()
