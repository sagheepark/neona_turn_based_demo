'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Brain, BookOpen, ChevronDown, ChevronUp, Tag } from 'lucide-react'

interface KnowledgeItem {
  id: string;
  title: string;
  content: string;
  tags: string[];
}

interface KnowledgeIndicatorProps {
  knowledge: KnowledgeItem[];
  isVisible: boolean;
  className?: string;
}

export function KnowledgeIndicator({ knowledge, isVisible, className = '' }: KnowledgeIndicatorProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [selectedKnowledge, setSelectedKnowledge] = useState<string | null>(null)

  if (!isVisible || knowledge.length === 0) {
    return null
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        transition={{ duration: 0.3 }}
        className={`mb-4 ${className}`}
      >
        <Card className="border-purple-200 bg-purple-50">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-600" />
                <CardTitle className="text-sm font-medium text-purple-900">
                  지식 베이스 활용됨
                </CardTitle>
                <span className="bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded-full">
                  {knowledge.length}개 항목
                </span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="h-8 w-8 p-0 text-purple-600 hover:bg-purple-100"
              >
                {isExpanded ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </Button>
            </div>
            <CardDescription className="text-purple-700">
              이 대화에서 관련 지식이 활용되었습니다
            </CardDescription>
          </CardHeader>

          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <CardContent className="pt-0 space-y-3">
                  {knowledge.map((item, index) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`border rounded-lg p-3 transition-all cursor-pointer ${
                        selectedKnowledge === item.id
                          ? 'border-purple-400 bg-white shadow-sm'
                          : 'border-purple-200 hover:border-purple-300 hover:bg-white/50'
                      }`}
                      onClick={() => setSelectedKnowledge(
                        selectedKnowledge === item.id ? null : item.id
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <BookOpen className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-purple-900 text-sm leading-tight">
                            {item.title}
                          </h4>
                          
                          {/* Tags */}
                          {item.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {item.tags.slice(0, 3).map((tag, tagIndex) => (
                                <span
                                  key={tagIndex}
                                  className="inline-flex items-center gap-1 bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded"
                                >
                                  <Tag className="w-3 h-3" />
                                  {tag}
                                </span>
                              ))}
                              {item.tags.length > 3 && (
                                <span className="text-purple-600 text-xs">
                                  +{item.tags.length - 3}개 더
                                </span>
                              )}
                            </div>
                          )}

                          {/* Expanded Content */}
                          <AnimatePresence>
                            {selectedKnowledge === item.id && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                transition={{ duration: 0.2 }}
                                className="overflow-hidden"
                              >
                                <div className="mt-3 pt-3 border-t border-purple-200">
                                  <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                                    {item.content}
                                  </div>
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </CardContent>
              </motion.div>
            )}
          </AnimatePresence>
        </Card>
      </motion.div>
    </AnimatePresence>
  )
}