import { cn } from "@/lib/utils";
import { Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import type { Components } from "react-markdown";

interface ChatBubbleProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
}

const ChatBubble = ({ message, isUser, timestamp }: ChatBubbleProps) => {
  return (
    <div
      className={cn(
        "flex gap-3 mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      <div
        className={cn(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
          isUser ? "bg-chat-user" : "bg-muted"
        )}
      >
        {isUser ? (
          <User className="w-5 h-5 text-primary-foreground" />
        ) : (
          <Bot className="w-5 h-5 text-primary" />
        )}
      </div>

      <div className={cn("flex flex-col max-w-[75%]", isUser && "items-end")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-3 shadow-sm",
            isUser
              ? "bg-chat-user text-primary-foreground rounded-tr-sm"
              : "bg-chat-assistant text-foreground rounded-tl-sm border"
          )}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message}</p>
          ) : (
            <div className="prose prose-sm max-w-none dark:prose-invert prose-headings:font-semibold prose-headings:text-foreground prose-p:text-foreground prose-p:leading-relaxed prose-strong:text-foreground prose-strong:font-semibold prose-ul:text-foreground prose-ol:text-foreground prose-li:text-foreground prose-li:leading-relaxed prose-a:text-primary prose-a:no-underline hover:prose-a:underline">
              <ReactMarkdown
                components={{
                  h3({ children, ...props }) {
                    return (
                      <h3 className="text-base font-semibold text-foreground mt-4 mb-2 first:mt-0" {...props}>
                        {children}
                      </h3>
                    );
                  },
                  ul({ children, ...props }) {
                    return (
                      <ul className="list-disc list-inside space-y-1 my-3 ml-4" {...props}>
                        {children}
                      </ul>
                    );
                  },
                  ol({ children, ...props }) {
                    return (
                      <ol className="list-decimal list-inside space-y-1 my-3 ml-4" {...props}>
                        {children}
                      </ol>
                    );
                  },
                  li({ children, ...props }) {
                    return (
                      <li className="text-foreground leading-relaxed" {...props}>
                        {children}
                      </li>
                    );
                  },
                  p({ children, ...props }) {
                    return (
                      <p className="text-foreground leading-relaxed mb-3 last:mb-0" {...props}>
                        {children}
                      </p>
                    );
                  },
                  strong({ children, ...props }) {
                    return (
                      <strong className="font-semibold text-foreground" {...props}>
                        {children}
                      </strong>
                    );
                  },
                  em({ children, ...props }) {
                    return (
                      <em className="italic text-muted-foreground text-sm" {...props}>
                        {children}
                      </em>
                    );
                  },
                  code({ className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || "");
                    const isInline = !match;

                    return !isInline ? (
                      <SyntaxHighlighter
                        style={vscDarkPlus as any}
                        language={match[1]}
                        PreTag="div"
                        className="rounded-md my-3"
                      >
                        {String(children).replace(/\n$/, "")}
                      </SyntaxHighlighter>
                    ) : (
                      <code
                        className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono text-foreground"
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  },
                  a({ children, href, ...props }) {
                    return (
                      <a
                        href={href}
                        className="text-primary hover:text-primary/80 underline underline-offset-2"
                        target="_blank"
                        rel="noopener noreferrer"
                        {...props}
                      >
                        {children}
                      </a>
                    );
                  },
                } as Components}
              >
                {message}
              </ReactMarkdown>
            </div>
          )}
        </div>
        {timestamp && (
          <span className="text-xs text-muted-foreground mt-1 px-2">
            {timestamp}
          </span>
        )}
      </div>
    </div>
  );
};

export default ChatBubble;
