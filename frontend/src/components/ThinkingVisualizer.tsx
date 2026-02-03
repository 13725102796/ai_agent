import { motion } from "framer-motion"
import { Brain, Search, PenTool, CheckCircle, Sparkles, Loader2, StopCircle } from "lucide-react"
import { useEffect, useRef } from "react"

interface StageContent {
  stage: string
  status: string
  streamingText: string
  completeText: string
}

interface ThinkingVisualizerProps {
  currentStage: string
  stageContents: Record<string, StageContent>
  onStop?: () => void
}

const steps = [
  { id: "researcher", icon: Search, label: "分析主题", desc: "Claude 收集背景资料..." },
  { id: "strategist", icon: Brain, label: "制定策略", desc: "Claude 选择写作风格与结构..." },
  { id: "writer", icon: PenTool, label: "撰写草稿", desc: "DeepSeek 创作初稿..." },
  { id: "editor", icon: Sparkles, label: "润色打磨", desc: "DeepSeek 优化语言与节奏..." },
]

export function ThinkingVisualizer({ currentStage, stageContents, onStop }: ThinkingVisualizerProps) {
  const activeIndex = steps.findIndex(s => s.id === currentStage)
  const streamRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when content updates
  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight
    }
  }, [stageContents])

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-8">
      {/* Progress Steps */}
      <div className="flex justify-between relative">
        {/* Connection Line */}
        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-slate-800 -z-10" />

        {steps.map((step, index) => {
          const isActive = step.id === currentStage
          const isCompleted = activeIndex > index || stageContents[step.id]?.status === 'complete'
          const isStreaming = stageContents[step.id]?.status === 'streaming'
          const Icon = isCompleted ? CheckCircle : (isStreaming ? Loader2 : step.icon)

          return (
            <div key={step.id} className="flex flex-col items-center gap-3 bg-transparent px-4">
              <motion.div
                initial={false}
                animate={{
                  backgroundColor: isActive ? "#6366f1" : (isCompleted ? "#10b981" : "#1e293b"),
                  scale: isActive ? 1.2 : 1
                }}
                className="w-12 h-12 rounded-full flex items-center justify-center border-4 border-slate-900 shadow-xl z-10"
              >
                <Icon className={`w-5 h-5 ${isCompleted ? "text-white" : "text-slate-300"} ${isStreaming ? "animate-spin" : ""}`} />
              </motion.div>
              <div className="text-center">
                <p className={`font-medium ${isActive ? "text-white" : "text-slate-500"}`}>{step.label}</p>
                {isActive && (
                  <motion.p
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-xs text-indigo-400 mt-1"
                  >
                    {step.desc}
                  </motion.p>
                )}
              </div>
            </div>
          )
        })}
      </div>



      {/* Streaming Content Display */}
      <div
        ref={streamRef}
        className="mt-8 bg-black/40 rounded-xl p-6 h-96 overflow-y-auto border border-white/5 text-sm"
      >
        {Object.entries(stageContents).map(([stageId, content]) => {
          const nodeNames: Record<string, string> = {
            researcher: "研究员",
            strategist: "策略师",
            writer: "作家",
            editor: "编辑"
          }
          const nodeName = nodeNames[stageId] || stageId

          return (
            <motion.div
              key={stageId}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-indigo-400 font-medium">[{nodeName}]</span>
                {content.status === 'streaming' && (
                  <Loader2 className="w-3 h-3 text-indigo-400 animate-spin" />
                )}
                {content.status === 'complete' && (
                  <CheckCircle className="w-3 h-3 text-green-400" />
                )}
              </div>
              <div className="text-slate-300 text-xs whitespace-pre-wrap leading-relaxed pl-4 border-l-2 border-indigo-500/30">
                {content.streamingText}
                {content.status === 'streaming' && (
                  <span className="inline-block w-2 h-4 bg-indigo-400 ml-1 animate-pulse" />
                )}
              </div>
            </motion.div>
          )
        })}

        {Object.keys(stageContents).length === 0 && (
          <div className="text-slate-600 italic text-center mt-20 flex flex-col items-center gap-3">
            <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
            等待灵感涌现...
          </div>
        )}
      </div>
      {/* Stop Button */}
      {onStop && (
        <div className="flex justify-center mt-6">
          <button
            onClick={onStop}
            className="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-full border border-red-500/30 transition-all text-sm font-medium"
          >
            <StopCircle className="w-4 h-4" />
            停止生成
          </button>
        </div>
      )}
    </div>
  )
}
