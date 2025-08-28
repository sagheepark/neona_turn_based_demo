'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Save, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react'

interface SelectiveConfigEditorProps {
  characterId: string
  characterName?: string
}

interface ParsedConfig {
  status_values: Record<string, any>
  milestones: Record<string, any>
  event_triggers: Record<string, any>
  memory_compression_prompt: string
  prompt_injection_template: string
}

export function SelectiveConfigEditor({ characterId, characterName }: SelectiveConfigEditorProps) {
  const [configText, setConfigText] = useState('')
  const [parsedConfig, setParsedConfig] = useState<ParsedConfig | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState<string[]>([])
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    loadConfig()
  }, [characterId])

  const loadConfig = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/characters/${characterId}/selective-config`)
      const data = await response.json()
      setConfigText(data.config_text || '')
      setParsedConfig(data.parsed || null)
      setErrors([])
    } catch (error) {
      console.error('Failed to load config:', error)
      setErrors(['Failed to load configuration'])
    } finally {
      setLoading(false)
    }
  }

  const saveConfig = async () => {
    setSaving(true)
    setSuccess(false)
    setErrors([])

    try {
      const response = await fetch(`http://localhost:8000/api/characters/${characterId}/selective-config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config_text: configText })
      })

      const data = await response.json()

      if (!response.ok) {
        setErrors(data.detail?.errors || ['Failed to save configuration'])
      } else {
        setParsedConfig(data.parsed_config)
        setSuccess(true)
        setTimeout(() => setSuccess(false), 3000)
      }
    } catch (error) {
      console.error('Failed to save config:', error)
      setErrors(['Failed to save configuration'])
    } finally {
      setSaving(false)
    }
  }

  const generateTemplate = (type: string) => {
    const templates: Record<string, string> = {
      companion: `# Status Values
affection: 0-100, default=50, "친밀도 수준"
trust: 0-100, default=30, "신뢰도"
mood: 0-100, default=70, "현재 기분"

# Milestones
first_meeting: "첫 만남" -> affection+5, trust+5
deep_conversation: "깊은 대화" -> affection+10, trust+15
shared_secret: "비밀 공유" -> trust+20, affection+10

# Event Triggers
user_compliment -> affection+5, mood+10
user_shares_problem -> trust+5, affection+3
long_conversation -> affection+2, trust+3

# Memory Compression Prompt
"대화에서 사용자의 감정 상태, 고민, 개인적 정보를 중심으로 요약하세요."

# Prompt Injection Template
"관계 상태: 친밀도 {affection}/100, 신뢰도 {trust}/100
현재 기분: {mood}/100
달성한 마일스톤: {milestones}
기억하는 정보: {persistent_facts}
이전 대화: {compressed_history}"`,

      teacher: `# Status Values
knowledge: 0-100, default=0, "지식 수준"
confidence: 0-100, default=30, "자신감"
progress: 0-100, default=0, "학습 진도"

# Milestones
first_lesson: "첫 수업 완료" -> confidence+10, progress+5
concept_mastered: "개념 마스터" -> knowledge+20, confidence+15
quiz_passed: "퀴즈 통과" -> progress+10, confidence+10

# Event Triggers
correct_answer -> knowledge+5, confidence+3
wrong_answer -> confidence-2
asks_question -> knowledge+2

# Memory Compression Prompt
"학습한 내용, 이해도, 어려워하는 부분을 중심으로 요약하세요."

# Prompt Injection Template
"학습 상태: 지식 {knowledge}/100, 자신감 {confidence}/100
진도: {progress}/100
달성 내역: {milestones}
학습 기록: {persistent_facts}
이전 수업: {compressed_history}"`
    }

    setConfigText(templates[type] || templates.companion)
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>
          Selective Knowledge Configuration
          {characterName && <span className="text-sm font-normal ml-2">for {characterName}</span>}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="editor" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="editor">Configuration Editor</TabsTrigger>
            <TabsTrigger value="preview">Parsed Preview</TabsTrigger>
          </TabsList>

          <TabsContent value="editor" className="space-y-4">
            <div className="flex gap-2 mb-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => generateTemplate('companion')}
              >
                Companion Template
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => generateTemplate('teacher')}
              >
                Teacher Template
              </Button>
            </div>

            <Textarea
              value={configText}
              onChange={(e) => setConfigText(e.target.value)}
              placeholder="Enter configuration text..."
              className="font-mono text-sm min-h-[400px]"
              disabled={loading}
            />

            {errors.length > 0 && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <ul className="list-disc pl-4">
                    {errors.map((error, i) => (
                      <li key={i}>{error}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert className="border-green-500 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  Configuration saved successfully!
                </AlertDescription>
              </Alert>
            )}

            <div className="flex gap-2">
              <Button
                onClick={saveConfig}
                disabled={saving || loading}
              >
                <Save className="mr-2 h-4 w-4" />
                {saving ? 'Saving...' : 'Save Configuration'}
              </Button>
              <Button
                variant="outline"
                onClick={loadConfig}
                disabled={loading}
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Reload
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="preview" className="space-y-4">
            {parsedConfig ? (
              <div className="space-y-4">
                {/* Status Values */}
                <div>
                  <h3 className="font-semibold mb-2">Status Values</h3>
                  <div className="bg-muted p-3 rounded-md space-y-1">
                    {Object.entries(parsedConfig.status_values).map(([key, value]: [string, any]) => (
                      <div key={key} className="text-sm">
                        <span className="font-medium">{key}:</span>{' '}
                        {value.min}-{value.max}, default={value.default}
                        {value.description && ` - "${value.description}"`}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Milestones */}
                <div>
                  <h3 className="font-semibold mb-2">Milestones</h3>
                  <div className="bg-muted p-3 rounded-md space-y-1">
                    {Object.entries(parsedConfig.milestones).map(([key, value]: [string, any]) => (
                      <div key={key} className="text-sm">
                        <span className="font-medium">{key}:</span> "{value.description}"
                        {value.rewards && Object.keys(value.rewards).length > 0 && (
                          <span className="text-muted-foreground ml-2">
                            → {Object.entries(value.rewards).map(([k, v]) => `${k}${v > 0 ? '+' : ''}${v}`).join(', ')}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Event Triggers */}
                <div>
                  <h3 className="font-semibold mb-2">Event Triggers</h3>
                  <div className="bg-muted p-3 rounded-md space-y-1">
                    {Object.entries(parsedConfig.event_triggers).map(([key, value]: [string, any]) => (
                      <div key={key} className="text-sm">
                        <span className="font-medium">{key}:</span>
                        <span className="text-muted-foreground ml-2">
                          → {Object.entries(value.impacts || {}).map(([k, v]) => 
                            typeof v === 'string' ? `${k}="${v}"` : `${k}${v > 0 ? '+' : ''}${v}`
                          ).join(', ')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Memory Compression Prompt */}
                {parsedConfig.memory_compression_prompt && (
                  <div>
                    <h3 className="font-semibold mb-2">Memory Compression Prompt</h3>
                    <div className="bg-muted p-3 rounded-md">
                      <p className="text-sm">{parsedConfig.memory_compression_prompt}</p>
                    </div>
                  </div>
                )}

                {/* Prompt Injection Template */}
                {parsedConfig.prompt_injection_template && (
                  <div>
                    <h3 className="font-semibold mb-2">Prompt Injection Template</h3>
                    <div className="bg-muted p-3 rounded-md">
                      <pre className="text-sm whitespace-pre-wrap">{parsedConfig.prompt_injection_template}</pre>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-muted-foreground">
                No parsed configuration available. Save the configuration to see the preview.
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}