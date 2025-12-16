"use client";

import {
  ArrowUp,
  AudioLinesIcon,
  MicIcon,
  Plus,
  Paperclip,
  Camera,
  Globe,
  RotateCcw,
  ChevronRight,
  Settings,
  FolderCode,
  X,
  Link as LinkIcon,
  MessageSquare,
  FileText,
} from "lucide-react";
import { Input } from "../ui/input";
import { useState, useRef, useEffect } from "react";
import clsx from "clsx";
import { motion, AnimatePresence } from "framer-motion";
import TickerAutocomplete, { Ticker } from "../chat/TickerAutocomplete";
import { useRouter } from "next/navigation";
import { useChats } from "@/hooks/chat";

export default function ChatInput({
  sendPrompt,
  onFocus,
  onBlur,
}: {
  sendPrompt: (message: string) => void;
  onFocus?: () => void;
  onBlur?: () => void;
}) {
  const [promptInput, setPromptInput] = useState("");
  const [cursorPosition, setCursorPosition] = useState(0);
  const [showTickerAutocomplete, setShowTickerAutocomplete] = useState(false);
  const [showPlusMenu, setShowPlusMenu] = useState(false);
  const [showWebpageModal, setShowWebpageModal] = useState(false);
  const [showReferenceChats, setShowReferenceChats] = useState(false);
  const [webpageUrl, setWebpageUrl] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [attachedWebpages, setAttachedWebpages] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const plusMenuRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const { chats } = useChats();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(); // prevent page reload

    // Build the message with attachments
    let message = promptInput.trim();

    // Add file references
    if (uploadedFiles.length > 0) {
      const fileRefs = uploadedFiles.map((f) => `[File: ${f.name}]`).join("\n");
      message = message ? `${message}\n${fileRefs}` : fileRefs;
    }

    // Add webpage references
    if (attachedWebpages.length > 0) {
      const webpageRefs = attachedWebpages
        .map((url) => `[Webpage: ${url}]`)
        .join("\n");
      message = message ? `${message}\n${webpageRefs}` : webpageRefs;
    }

    if (!message.trim()) return;

    sendPrompt(message); // send text with attachments
    setPromptInput(""); // clear input after sending
    setUploadedFiles([]); // clear uploaded files
    setAttachedWebpages([]); // clear attached webpages
    setShowTickerAutocomplete(false);
  };

  const handleBlur = () => {
    // Delay closing autocomplete to allow click events
    setTimeout(() => {
      setShowTickerAutocomplete(false);
    }, 200);

    // Only call onBlur if input is empty (bring widgets back)
    if (promptInput.trim() === "" && onBlur) {
      onBlur();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const position = e.target.selectionStart || 0;

    setPromptInput(value);
    setCursorPosition(position);

    // Check if @ symbol is present and cursor is after it
    const textBeforeCursor = value.substring(0, position);
    const atIndex = textBeforeCursor.lastIndexOf("@");
    const hasSpaceAfterAt = textBeforeCursor
      .substring(atIndex + 1)
      .includes(" ");

    if (atIndex !== -1 && !hasSpaceAfterAt && position > atIndex) {
      setShowTickerAutocomplete(true);
    } else {
      setShowTickerAutocomplete(false);
    }
  };

  const handleTickerSelect = (ticker: Ticker) => {
    const textBeforeCursor = promptInput.substring(0, cursorPosition);
    const atIndex = textBeforeCursor.lastIndexOf("@");

    if (atIndex === -1) return;

    const textBeforeAt = promptInput.substring(0, atIndex);
    const textAfterCursor = promptInput.substring(cursorPosition);
    const newText = `${textBeforeAt}@${ticker.symbol} ${textAfterCursor}`;

    setPromptInput(newText);
    setShowTickerAutocomplete(false);

    // Set cursor position after the inserted ticker
    setTimeout(() => {
      if (inputRef.current) {
        const newPosition = atIndex + ticker.symbol.length + 2; // +2 for @ and space
        inputRef.current.setSelectionRange(newPosition, newPosition);
        inputRef.current.focus();
      }
    }, 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Don't interfere with autocomplete keyboard navigation
    if (
      showTickerAutocomplete &&
      (e.key === "ArrowDown" ||
        e.key === "ArrowUp" ||
        e.key === "Enter" ||
        e.key === "Tab")
    ) {
      return; // Let TickerAutocomplete handle it
    }

    setCursorPosition(e.currentTarget.selectionStart || 0);
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (
        plusMenuRef.current &&
        !plusMenuRef.current.contains(target) &&
        !target.closest("[data-plus-button]")
      ) {
        setShowPlusMenu(false);
      }
    };

    if (showPlusMenu) {
      // Use a small delay to prevent flickering
      const timeoutId = setTimeout(() => {
        document.addEventListener("mousedown", handleClickOutside);
      }, 100);

      return () => {
        clearTimeout(timeoutId);
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }
  }, [showPlusMenu]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const newFiles = Array.from(files);
      setUploadedFiles((prev) => [...prev, ...newFiles]);
      // Don't add file info to input text - files are displayed separately
    }
    // Reset file input to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleScreenshot = async () => {
    try {
      // Check if Screen Capture API is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        alert(
          "Screen capture is not supported in your browser. Please use a modern browser like Chrome, Firefox, or Edge."
        );
        return;
      }

      // Request screen capture - browser will show dialog to select screen/window/tab
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: false,
      });

      // Create video element to capture the stream
      const video = document.createElement("video");
      video.srcObject = stream;
      video.autoplay = true;
      video.playsInline = true;

      // Wait for video to be ready and play
      await new Promise<void>((resolve, reject) => {
        video.onloadedmetadata = () => {
          video
            .play()
            .then(() => {
              // Wait a moment for the video to render
              setTimeout(() => {
                resolve();
              }, 100);
            })
            .catch(reject);
        };
        video.onerror = reject;
      });

      // Create canvas to capture the frame
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");

      if (!ctx) {
        stream.getTracks().forEach((track) => track.stop());
        return;
      }

      // Draw video frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Stop the stream immediately after capturing
      stream.getTracks().forEach((track) => track.stop());

      // Clean up video element
      video.srcObject = null;

      // Convert canvas to blob
      canvas.toBlob((blob) => {
        if (!blob) return;

        // Create a File object from the blob
        const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
        const fileName = `screenshot-${timestamp}.png`;
        const file = new File([blob], fileName, { type: "image/png" });

        // Add to uploaded files
        setUploadedFiles((prev) => [...prev, file]);
        // Don't add to input text - files are displayed separately
      }, "image/png");
    } catch (error: any) {
      // User cancelled or error occurred
      if (error.name !== "NotAllowedError" && error.name !== "AbortError") {
        console.error("Screenshot error:", error);
        alert("Failed to capture screenshot. Please try again.");
      }
      // Silently handle cancellation (user clicked cancel in browser dialog)
    }
  };

  const handleAttachWebpage = () => {
    if (webpageUrl.trim()) {
      setAttachedWebpages((prev) => [...prev, webpageUrl.trim()]);
      // Don't add to input text - webpages are displayed separately
      setWebpageUrl("");
      setShowWebpageModal(false);
    }
  };

  const handleReferenceChat = (chatId: string) => {
    const urlText = `[Reference Chat: /c/${chatId}]`;
    setPromptInput((prev) => (prev ? `${prev}\n${urlText}` : urlText));
    setShowReferenceChats(false);
  };

  const menuItems = [
    {
      icon: Paperclip,
      label: "Upload Files",
      onClick: () => {
        fileInputRef.current?.click();
        setShowPlusMenu(false);
      },
    },
    {
      icon: Camera,
      label: "Capture",
      onClick: () => {
        handleScreenshot();
        setShowPlusMenu(false);
      },
    },
    {
      icon: Globe,
      label: "Attach Webpage",
      onClick: () => {
        setShowWebpageModal(true);
        setShowPlusMenu(false);
      },
    },
    {
      icon: RotateCcw,
      label: "Reference Chats",
      onClick: () => {
        setShowReferenceChats(true);
        setShowPlusMenu(false);
      },
      hasArrow: true,
    },
  ];

  const actionIcons = [
    {
      icon: Paperclip,
      label: "Upload Files",
      onClick: () => {
        fileInputRef.current?.click();
      },
    },
    {
      icon: Globe,
      label: "Attach Webpage",
      onClick: () => {
        setShowWebpageModal(true);
      },
    },
    {
      icon: Settings,
      label: "Settings",
      onClick: () => {
        router.push("/profile");
      },
    },
    {
      icon: FolderCode,
      label: "Reference Chats",
      onClick: () => {
        setShowReferenceChats(true);
      },
    },
  ];

  return (
    <motion.div
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="w-full"
    >
      <motion.form
        onSubmit={handleSubmit}
        className="w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <motion.div
          className="flex p-2 w-[100%] items-center rounded-3xl glass-input relative"
          whileHover={{
            scale: 1.02,
            rotateY: 2,
            transition: { duration: 0.2 },
          }}
          whileFocus={{
            scale: 1.03,
            rotateY: 0,
            transition: { duration: 0.2 },
          }}
          style={{
            transformStyle: "preserve-3d",
          }}
        >
          <div
            className="relative ml-2 z-10"
            data-plus-button
            onMouseLeave={(e) => {
              // Only close if we're leaving the entire button+menu area
              const relatedTarget = e.relatedTarget as HTMLElement | null;

              // If no related target (mouse left the window), close menu
              if (!relatedTarget) {
                setShowPlusMenu(false);
                return;
              }

              // Check if relatedTarget is a valid Node before using contains
              if (relatedTarget instanceof Node) {
                const isInMenu = plusMenuRef.current?.contains(relatedTarget);
                const isInButtonArea =
                  relatedTarget.closest("[data-plus-button]");

                // Only close if we're not moving to menu or button area
                if (!isInMenu && !isInButtonArea) {
                  setShowPlusMenu(false);
                }
              } else {
                // If not a valid Node, close menu
                setShowPlusMenu(false);
              }
            }}
          >
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setShowPlusMenu((prev) => {
                  const newState = !prev;
                  return newState;
                });
              }}
              className="flex items-center justify-center w-8 h-8 rounded-lg bg-[var(--tradeberg-glass-bg)] border border-[var(--tradeberg-glass-border)] hover:bg-[var(--tradeberg-card-bg)] transition-all cursor-pointer backdrop-blur-sm"
              style={{
                boxShadow: "0 2px 8px 0 var(--tradeberg-shadow)",
                zIndex: 10,
                position: "relative",
              }}
            >
              <Plus
                className="text-[var(--tradeberg-text-secondary)] w-4 h-4 pointer-events-none"
                strokeWidth={1.5}
              />
            </button>

            <AnimatePresence>
              {showPlusMenu && (
                <motion.div
                  ref={plusMenuRef}
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="absolute bottom-full left-0 mb-1 w-56 bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-glass-border)] rounded-lg shadow-lg overflow-hidden z-50"
                  style={{
                    backdropFilter: "blur(10px)",
                  }}
                >
                  {menuItems.map((item, index) => {
                    const Icon = item.icon;
                    return (
                      <button
                        key={index}
                        type="button"
                        onClick={item.onClick}
                        className="w-full flex items-center gap-3 px-4 py-3 text-left text-[var(--tradeberg-text-primary)] hover:bg-[var(--tradeberg-glass-bg)] transition-colors first:rounded-t-lg last:rounded-b-lg"
                      >
                        <Icon className="w-5 h-5 flex-shrink-0" />
                        <span className="flex-1 text-sm">{item.label}</span>
                        {item.hasArrow && (
                          <ChevronRight className="w-4 h-4 text-[var(--tradeberg-text-secondary)]" />
                        )}
                      </button>
                    );
                  })}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="relative flex-1">
            <Input
              ref={inputRef}
              className="border-0 shadow-none outline-0 focus-visible:ring-0 bg-transparent text-foreground placeholder:text-muted-foreground w-full"
              type="text"
              placeholder="Ask anything (type @ for tickers)"
              value={promptInput}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={(e) => {
                setCursorPosition(e.target.selectionStart || 0);
                onFocus?.();
              }}
              onBlur={handleBlur}
              onClick={(e) => {
                setCursorPosition(
                  (e.target as HTMLInputElement).selectionStart || 0
                );
              }}
            />
            <AnimatePresence>
              {showTickerAutocomplete && (
                <TickerAutocomplete
                  value={promptInput}
                  cursorPosition={cursorPosition}
                  onSelect={handleTickerSelect}
                  onClose={() => setShowTickerAutocomplete(false)}
                  inputRef={inputRef}
                  showTickerAutocomplete={showTickerAutocomplete}
                />
              )}
            </AnimatePresence>
          </div>

          <div className="mr-2 cursor-pointer">
            <MicIcon
              height={20}
              width={20}
              className="text-gray-700 dark:text-gray-400"
              strokeWidth={1.5}
            />
          </div>

          <motion.div
            className={clsx(
              "flex p-2 rounded-[100%] cursor-pointer transition-all duration-200",
              {
                "bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-500/50":
                  promptInput.length > 0,
                "glass-light hover:glass": promptInput.length === 0,
              }
            )}
            whileHover={{
              scale: 1.1,
              rotateY: 10,
              transition: { duration: 0.2 },
            }}
            whileTap={{
              scale: 0.95,
              rotateY: -5,
              transition: { duration: 0.1 },
            }}
            style={{
              transformStyle: "preserve-3d",
            }}
          >
            {promptInput.length > 0 ? (
              <motion.button
                type="submit"
                whileHover={{
                  rotateZ: 360,
                  transition: { duration: 0.5 },
                }}
              >
                <ArrowUp height={20} width={20} className="text-white" />
              </motion.button>
            ) : (
              <AudioLinesIcon
                height={20}
                width={20}
                className="text-gray-700 dark:text-gray-400"
                strokeWidth={1.5}
              />
            )}
          </motion.div>
        </motion.div>
      </motion.form>

      {/* Action Icons Row */}
      <div className="flex items-center justify-center gap-0 mt-2 px-2">
        {actionIcons.map((item, index) => {
          const Icon = item.icon;
          return (
            <div key={index} className="flex items-center">
              <button
                type="button"
                onClick={item.onClick}
                className="p-2 text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] transition-colors"
                title={item.label}
              >
                <Icon className="w-5 h-5" strokeWidth={1.5} />
              </button>
              {index < actionIcons.length - 1 && (
                <div className="h-4 w-px bg-[var(--tradeberg-glass-border)] mx-1" />
              )}
            </div>
          );
        })}
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileUpload}
        className="hidden"
        accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt,.csv"
      />

      {/* Webpage Attachment Modal */}
      <AnimatePresence>
        {showWebpageModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowWebpageModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-glass-border)] rounded-lg p-6 w-full max-w-md shadow-xl"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-[var(--tradeberg-text-primary)] flex items-center gap-2">
                  <LinkIcon className="w-5 h-5" />
                  Attach Webpage
                </h3>
                <button
                  onClick={() => setShowWebpageModal(false)}
                  className="text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="space-y-4">
                <Input
                  type="url"
                  placeholder="https://example.com"
                  value={webpageUrl}
                  onChange={(e) => setWebpageUrl(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleAttachWebpage();
                    }
                  }}
                  className="bg-[var(--tradeberg-glass-bg)] border-[var(--tradeberg-glass-border)] text-[var(--tradeberg-text-primary)] placeholder:text-[var(--tradeberg-text-secondary)] focus:border-[var(--tradeberg-accent-color)] focus:ring-2 focus:ring-[var(--tradeberg-accent-color)]/20"
                />
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={() => setShowWebpageModal(false)}
                    className="px-4 py-2 text-sm text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAttachWebpage}
                    disabled={!webpageUrl.trim()}
                    className="px-4 py-2 text-sm bg-[var(--tradeberg-accent-color)] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Attach
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Reference Chats Modal */}
      <AnimatePresence>
        {showReferenceChats && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowReferenceChats(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-glass-border)] rounded-lg p-6 w-full max-w-md shadow-xl max-h-[80vh] flex flex-col"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-[var(--tradeberg-text-primary)] flex items-center gap-2">
                  <FolderCode className="w-5 h-5" />
                  Reference Chats
                </h3>
                <button
                  onClick={() => setShowReferenceChats(false)}
                  className="text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto show-scrollbar-on-hover">
                {chats && chats.length > 0 ? (
                  <div className="space-y-2">
                    {chats.map((chat) => (
                      <button
                        key={chat.id}
                        onClick={() => handleReferenceChat(chat.id)}
                        className="w-full text-left p-3 rounded-lg hover:bg-[var(--tradeberg-glass-bg)] transition-colors flex items-center gap-3"
                      >
                        <MessageSquare className="w-4 h-4 text-[var(--tradeberg-text-secondary)] flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-[var(--tradeberg-text-primary)] truncate">
                            {chat.title}
                          </p>
                          {chat.preview && (
                            <p className="text-xs text-[var(--tradeberg-text-secondary)] truncate">
                              {chat.preview}
                            </p>
                          )}
                        </div>
                        <ChevronRight className="w-4 h-4 text-[var(--tradeberg-text-secondary)] flex-shrink-0" />
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <MessageSquare className="w-12 h-12 text-[var(--tradeberg-text-secondary)] mx-auto mb-3 opacity-50" />
                    <p className="text-sm text-[var(--tradeberg-text-secondary)]">
                      No previous chats to reference
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Attached Files and Webpages Display */}
      {(uploadedFiles.length > 0 || attachedWebpages.length > 0) && (
        <div className="mt-3 px-2 space-y-2">
          {/* Uploaded Files */}
          {uploadedFiles.map((file, index) => {
            const getFileType = (fileName: string) => {
              const ext = fileName.split(".").pop()?.toLowerCase();
              if (
                ["jpg", "jpeg", "png", "gif", "webp", "svg"].includes(ext || "")
              )
                return "Image";
              if (["mp4", "avi", "mov", "webm"].includes(ext || ""))
                return "Video";
              if (["mp3", "wav", "ogg"].includes(ext || "")) return "Audio";
              if (ext === "pdf") return "PDF";
              if (["doc", "docx"].includes(ext || "")) return "Document";
              if (["txt", "csv"].includes(ext || "")) return "Text";
              return "File";
            };

            return (
              <motion.div
                key={`file-${index}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-3 px-4 py-3 bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-glass-border)] rounded-lg hover:bg-[var(--tradeberg-glass-bg)] transition-colors group"
              >
                <FileText className="w-5 h-5 text-[var(--tradeberg-text-secondary)] flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-[var(--tradeberg-text-primary)] truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-[var(--tradeberg-text-secondary)]">
                    {getFileType(file.name)}
                  </p>
                </div>
                <button
                  onClick={() => {
                    const newFiles = uploadedFiles.filter(
                      (_, i) => i !== index
                    );
                    setUploadedFiles(newFiles);
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            );
          })}

          {/* Attached Webpages */}
          {attachedWebpages.map((url, index) => (
            <motion.div
              key={`webpage-${index}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3 px-4 py-3 bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-glass-border)] rounded-lg hover:bg-[var(--tradeberg-glass-bg)] transition-colors group"
            >
              <LinkIcon className="w-5 h-5 text-[var(--tradeberg-text-secondary)] flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-[var(--tradeberg-text-primary)] truncate">
                  {url.length > 50 ? `${url.substring(0, 50)}...` : url}
                </p>
                <p className="text-xs text-[var(--tradeberg-text-secondary)]">
                  Webpage
                </p>
              </div>
              <button
                onClick={() => {
                  const newWebpages = attachedWebpages.filter(
                    (_, i) => i !== index
                  );
                  setAttachedWebpages(newWebpages);
                }}
                className="opacity-0 group-hover:opacity-100 transition-opacity text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
