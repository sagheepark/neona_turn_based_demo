'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { 
  ChevronDown, 
  ChevronUp, 
  Trophy, 
  Brain, 
  Heart,
  Zap,
  TrendingUp,
  TrendingDown
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface StatusValue {
  current: number
  min: number
  max: number
  description?: string
}

interface Milestone {
  id: string
  description: string
  achieved_at: string
}

interface Event {
  timestamp: string
  event_type: string
  description: string
  impact?: Record<string, number>
}

interface CoreMemory {
  status_values: Record<string, number>
  milestones: Milestone[]
  event_log: Event[]
  persistent_facts: string[]
  conversation_count: number
}

interface MemoryStatusDisplayProps {
  characterId: string
  userId: string
  className?: string
}

export function MemoryStatusDisplay({ 
  characterId, 
  userId, 
  className 
}: MemoryStatusDisplayProps) {
  const [coreMemory, setCoreMemory] = useState<CoreMemory | null>(null)
  const [config, setConfig] = useState<any>(null)
  const [expanded, setExpanded] = useState(false)
  const [loading, setLoading] = useState(true)
  const [previousValues, setPreviousValues] = useState<Record<string, number>>({})

  useEffect(() => {
    loadMemory()
    // Poll for updates every 5 seconds during active chat
    const interval = setInterval(loadMemory, 5000)
    return () => clearInterval(interval)
  }, [characterId, userId])

  const loadMemory = async () => {
    try {
      // Load memory
      const memoryResponse = await fetch(
        `http://localhost:8000/api/memory/${characterId}/${userId}`
      )
      const memoryData = await memoryResponse.json()
      
      // Track value changes for animations
      if (coreMemory) {
        setPreviousValues(coreMemory.status_values)
      }
      
      setCoreMemory(memoryData.core_memory)

      // Load config for status definitions
      const configResponse = await fetch(
        `http://localhost:8000/api/characters/${characterId}/selective-config`
      )
      const configData = await configResponse.json()
      setConfig(configData.parsed)
    } catch (error) {
      console.error('Failed to load memory:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (name: string) => {
    const icons: Record<string, any> = {
      affection: Heart,
      trust: Brain,
      stress: Zap,
      knowledge: Brain,
      energy: Zap
    }
    const Icon = icons[name.toLowerCase()] || Brain
    return <Icon className="h-3 w-3" />
  }

  const getValueChange = (name: string, current: number) => {
    const previous = previousValues[name]
    if (previous === undefined) return 0
    return current - previous
  }

  if (loading) {
    return (
      <Card className={cn("animate-pulse", className)}>
        <CardContent className="p-3">
          <div className="h-20 bg-muted rounded" />
        </CardContent>
      </Card>
    )
  }

  if (!coreMemory || !config) {
    return null
  }

  return (
    <Card className={cn("transition-all duration-300", className)}>
      <CardContent className="p-3">
        {/* Compact View */}
        <div className="space-y-2">
          {/* Status Bars */}
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(coreMemory.status_values).slice(0, 4).map(([name, value]) => {
              const statusDef = config.status_values?.[name] || {}
              const change = getValueChange(name, value)
              const percentage = ((value - (statusDef.min || 0)) / ((statusDef.max || 100) - (statusDef.min || 0))) * 100

              return (
                <div key={name} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      {getStatusIcon(name)}
                      <span className="text-xs font-medium capitalize">{name}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-xs font-bold">{value}</span>
                      {change !== 0 && (
                        <span className={cn(
                          "text-xs",
                          change > 0 ? "text-green-500" : "text-red-500"
                        )}>
                          {change > 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                        </span>
                      )}
                    </div>
                  </div>
                  <Progress 
                    value={percentage} 
                    className="h-1.5"
                  />
                </div>
              )
            })}
          </div>

          {/* Recent Milestone */}
          {coreMemory.milestones.length > 0 && (
            <div className="flex items-center gap-2 pt-1">
              <Trophy className="h-3 w-3 text-yellow-500" />
              <span className="text-xs text-muted-foreground">
                {coreMemory.milestones[coreMemory.milestones.length - 1].description}
              </span>
            </div>
          )}

          {/* Expand/Collapse Button */}
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center justify-center w-full py-1 hover:bg-muted/50 rounded transition-colors"
          >
            {expanded ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            )}
          </button>
        </div>

        {/* Expanded View */}
        {expanded && (
          <div className="mt-3 pt-3 border-t space-y-3">
            {/* All Milestones */}
            <div>
              <h4 className="text-xs font-semibold mb-1">Milestones</h4>
              <div className="space-y-1">
                {coreMemory.milestones.map((milestone) => (
                  <div key={milestone.id} className="flex items-center gap-2">
                    <Trophy className="h-3 w-3 text-yellow-500" />
                    <span className="text-xs">{milestone.description}</span>
                  </div>
                ))}
                {coreMemory.milestones.length === 0 && (
                  <span className="text-xs text-muted-foreground">No milestones yet</span>
                )}
              </div>
            </div>

            {/* Recent Events */}
            <div>
              <h4 className="text-xs font-semibold mb-1">Recent Events</h4>
              <div className="space-y-1 max-h-20 overflow-y-auto">
                {coreMemory.event_log.slice(-3).reverse().map((event, i) => (
                  <div key={i} className="text-xs text-muted-foreground">
                    {event.description}
                  </div>
                ))}
                {coreMemory.event_log.length === 0 && (
                  <span className="text-xs text-muted-foreground">No events recorded</span>
                )}
              </div>
            </div>

            {/* Persistent Facts */}
            {coreMemory.persistent_facts.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold mb-1">Remembered Facts</h4>
                <div className="space-y-1">
                  {coreMemory.persistent_facts.slice(0, 3).map((fact, i) => (
                    <div key={i} className="text-xs text-muted-foreground">
                      • {fact}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Session Info */}
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Conversations: {coreMemory.conversation_count}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}