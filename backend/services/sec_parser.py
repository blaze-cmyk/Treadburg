"""
SEC Data Parser for extracting financial metrics from XBRL data.
"""

from typing import Dict, List, Optional


def extract_financials(company_facts: Dict) -> Dict:
    """
    Extract key financial metrics from SEC company facts
    
    Args:
        company_facts: Raw company facts data from SEC API
        
    Returns:
        Structured financial data with revenues, net income, etc.
    """
    if not company_facts:
        return {}
    
    result = {
        'name': company_facts.get('entityName', 'Unknown'),
        'cik': company_facts.get('cik', ''),
        'revenues': [],
        'netIncome': [],
        'operatingIncome': []
    }
    
    facts = company_facts.get('facts', {})
    us_gaap = facts.get('us-gaap', {})
    
    # Extract Revenues
    # Try different common tags for Revenue (it varies by industry)
    revenues_data = (
        us_gaap.get('Revenues', {}) or 
        us_gaap.get('SalesRevenueNet', {}) or 
        us_gaap.get('RevenueFromContractWithCustomerExcludingAssessedTax', {})
    )
    
    if revenues_data:
        units = revenues_data.get('units', {})
        usd_data = units.get('USD', [])
        result['revenues'] = _process_financial_data(usd_data)
    
    # Extract Net Income/Loss
    net_income_data = us_gaap.get('NetIncomeLoss', {})
    if net_income_data:
        units = net_income_data.get('units', {})
        usd_data = units.get('USD', [])
        result['netIncome'] = _process_financial_data(usd_data)
    
    # Extract Operating Income/Loss
    operating_income_data = us_gaap.get('OperatingIncomeLoss', {})
    if operating_income_data:
        units = operating_income_data.get('units', {})
        usd_data = units.get('USD', [])
        result['operatingIncome'] = _process_financial_data(usd_data)
    
    return result


def _process_financial_data(usd_data: List[Dict]) -> List[Dict]:
    """
    Process USD financial data into a clean format
    
    Args:
        usd_data: List of financial data points
        
    Returns:
        Processed list with period and value
    """
    processed = []
    seen_periods = set()
    
    # Sort by date descending (newest first)
    # Handle cases where 'end' date might be missing
    sorted_data = sorted(
        [x for x in usd_data if x.get('end')],
        key=lambda x: x.get('end', ''),
        reverse=True
    )
    
    for item in sorted_data:
        # Include 10-K (Annual) and 10-Q (Quarterly)
        form = item.get('form')
        if form not in ['10-K', '10-Q']:
            continue
        
        # Get fiscal year and period
        fy = item.get('fy')
        fp = item.get('fp')
        val = item.get('val')
        
        if not all([fy, fp, val]):
            continue
        
        # Create period label
        # If frame is present, use it (e.g. CY2023Q1), else construct it
        frame = item.get('frame')
        if frame:
            period = frame
        elif form == '10-K':
            period = f"FY{fy}"
        else:
            period = f"{fp}{fy}"
        
        # Avoid duplicates
        if period in seen_periods:
            continue
        
        seen_periods.add(period)
        processed.append({
            'period': period,
            'value': val / 1_000_000_000,  # Convert to billions
            'fiscalYear': fy,
            'fiscalPeriod': fp,
            'form': form,
            'date': item.get('end')
        })
    
    return processed
