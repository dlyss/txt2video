import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "txt2video",
  description: "Script to short video MVP"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh">
      <body>
        <div className="container">
          <header className="header">
            <h1>txt2video MVP</h1>
            <nav>
              <a href="/" style={{ marginRight: 12 }}>首页</a>
              <a href="/settings">设置</a>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
