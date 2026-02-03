import { useState } from "react"
import { Search } from "lucide-react"
import { Button } from "./ui/button"

interface InputZoneProps {
    onStart: (topic: string) => void
}

export function InputZone({ onStart }: InputZoneProps) {
    const [topic, setTopic] = useState("")

    const handleStart = () => {
        if (topic.trim()) onStart(topic)
    }

    const styles = [
        "散文随笔 (Poetic)",
        "深度长文 (Deep)",
        "未来主义 (Visionary)",
        "辛辣评论 (Critical)"
    ]

    return (
        <div className="flex flex-col items-center justify-center space-y-8 animate-fade-in-up">
            <div className="text-center space-y-2">
                <h1 className="text-4xl font-semibold tracking-tight text-white drop-shadow-glow">
                    What shall we create today?
                </h1>
                <p className="text-slate-400">Enter a topic, and I will research, plan, and write it for you.</p>
            </div>

            <div className="w-full max-w-2xl relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                <div className="relative flex items-center bg-surface border border-white/10 rounded-2xl p-2 shadow-2xl">
                    <Search className="ml-4 h-6 w-6 text-slate-400" />
                    <input
                        type="text"
                        className="flex-1 bg-transparent border-none outline-none text-lg px-4 py-3 placeholder:text-slate-600 text-white"
                        placeholder="e.g. The solitude of automation..."
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleStart()}
                    />
                    <Button onClick={handleStart} className="rounded-xl px-6 py-6 text-lg">
                        Create
                    </Button>
                </div>
            </div>

            <div className="flex gap-3">
                {styles.map((s) => (
                    <button
                        key={s}
                        onClick={() => setTopic(prev => prev + (prev ? " " : "") + `[Style: ${s}]`)}
                        className="px-4 py-2 rounded-full border border-white/10 bg-white/5 text-sm text-slate-300 hover:bg-white/10 hover:border-indigo-500/50 transition-all cursor-pointer"
                    >
                        {s}
                    </button>
                ))}
            </div>
        </div>
    )
}
