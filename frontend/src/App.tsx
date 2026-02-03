import { useState } from 'react'
import { InputZone } from './components/InputZone'
import { ThinkingVisualizer } from './components/ThinkingVisualizer'
import { ArticleView } from './components/ArticleView'
import { Sparkles } from 'lucide-react'

// Backend URL
const API_URL = "http://127.0.0.1:8000"

// Stage content type
interface StageContent {
  stage: string
  status: string
  streamingText: string
  completeText: string
}

function App() {
  const [appStage, setAppStage] = useState<"input" | "thinking" | "reading">("input")
  const [currentStage, setCurrentStage] = useState<string>("researcher")
  const [stageContents, setStageContents] = useState<Record<string, StageContent>>({})
  const [finalArticle, setFinalArticle] = useState("")
  const [topic, setTopic] = useState("")
  const [abortController, setAbortController] = useState<AbortController | null>(null)

  const startCreation = async (userTopic: string) => {
    setTopic(userTopic)
    setAppStage("thinking")
    setStageContents({})
    setCurrentStage("researcher")


    const controller = new AbortController()
    setAbortController(controller)

    try {
      const response = await fetch(`${API_URL}/stream_generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: userTopic }),
        signal: controller.signal
      })

      if (!response.body) return

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split("\n\n")

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "")
            if (dataStr === "[DONE]") {
              break
            }
            try {
              const data = JSON.parse(dataStr)
              console.log("Stream update:", data)

              const { stage, status, delta, content, message, final_article } = data

              if (stage === "done" && final_article) {
                setFinalArticle(final_article)
                setTimeout(() => setAppStage("reading"), 1500)
                continue
              }

              if (stage) {
                setCurrentStage(stage)

                setStageContents(prev => {
                  const existing = prev[stage] || { stage, status: '', streamingText: '', completeText: '' }

                  if (status === 'start') {
                    return {
                      ...prev,
                      [stage]: { ...existing, status: 'start', streamingText: message || '' }
                    }
                  } else if (status === 'streaming' && delta) {
                    return {
                      ...prev,
                      [stage]: { ...existing, status: 'streaming', streamingText: existing.streamingText + delta }
                    }
                  } else if (status === 'complete' && content) {
                    return {
                      ...prev,
                      [stage]: { ...existing, status: 'complete', completeText: content, streamingText: content }
                    }
                  }
                  return prev
                })
              }
            } catch (e) {
              console.error("Parse error", e)
            }
          }
        }
      }
    } catch (e) {
      console.error("Error starting generation", e)
    }
  }

  const stopCreation = () => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
      // Optionally reset to input or show a stopped state
      // For now, let's just stay in 'thinking' but maybe show a message
      console.log("Generation stopped by user")
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-[#0f172a] to-[#1e1b4b] text-slate-50 overflow-x-hidden font-sans selection:bg-indigo-500/30">

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 p-6 z-50 flex items-center justify-between">
        <div className="flex items-center gap-2 font-serif font-bold text-xl tracking-wider text-white/80">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          LitAgent
        </div>
        {appStage !== "input" && (
          <button onClick={() => window.location.reload()} className="text-xs text-white/50 hover:text-white transition-colors uppercase tracking-widest">
            重新开始
          </button>
        )}
      </header>

      {/* Main Content Areas */}
      <main className="container mx-auto px-4 min-h-screen flex flex-col items-center justify-center pt-20">

        {appStage === "input" && (
          <InputZone onStart={startCreation} />
        )}

        {appStage === "thinking" && (
          <ThinkingVisualizer
            currentStage={currentStage}
            stageContents={stageContents}
            onStop={stopCreation}
          />
        )}

        {appStage === "reading" && (
          <ArticleView title={topic} content={finalArticle} />
        )}

      </main>

      {/* Background Ambience */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[128px] animate-pulse-glow" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[128px]" />
      </div>
    </div>
  )
}

export default App
