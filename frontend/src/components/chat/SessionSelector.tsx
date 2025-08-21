'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { SessionStartResponse } from '@/lib/api-client'
import { MessageCircle, Plus, Calendar, ArrowRight } from 'lucide-react'

interface SessionSelectorProps {
  sessionData: SessionStartResponse;
  onContinueSession: (sessionId: string) => void;
  onCreateNew: () => void;
  characterName: string;
}

export function SessionSelector({ 
  sessionData, 
  onContinueSession, 
  onCreateNew, 
  characterName 
}: SessionSelectorProps) {
  const [selectedSession, setSelectedSession] = useState<string | null>(null)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatMessagePreview = (message: string, maxLength: number = 50) => {
    return message.length > maxLength 
      ? message.substring(0, maxLength) + '...' 
      : message
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-4">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {characterName}와의 대화
          </h1>
          <p className="text-gray-600">
            이전 대화를 계속하거나 새로운 대화를 시작하세요
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Create New Session Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="h-full border-2 border-green-200 hover:border-green-300 transition-colors cursor-pointer"
                  onClick={onCreateNew}>
              <CardHeader className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Plus className="w-8 h-8 text-green-600" />
                </div>
                <CardTitle className="text-green-700">새로운 대화 시작</CardTitle>
                <CardDescription>
                  처음부터 새로운 대화를 시작합니다
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                <Button className="w-full bg-green-600 hover:bg-green-700">
                  새 대화 시작
                </Button>
              </CardContent>
            </Card>
          </motion.div>

          {/* Previous Sessions */}
          {sessionData.data.can_continue && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="h-full">
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <MessageCircle className="w-5 h-5 text-blue-600" />
                    <CardTitle className="text-blue-700">이전 대화 계속하기</CardTitle>
                  </div>
                  <CardDescription>
                    {sessionData.data.previous_sessions.length}개의 이전 대화가 있습니다
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {sessionData.data.previous_sessions.map((session, index) => (
                    <motion.div
                      key={session.session_id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + index * 0.1 }}
                      className={`p-3 border rounded-lg cursor-pointer transition-all ${
                        selectedSession === session.session_id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                      }`}
                      onClick={() => setSelectedSession(session.session_id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <Calendar className="w-4 h-4 text-gray-500" />
                            <span className="text-sm text-gray-600">
                              {formatDate(session.last_updated)}
                            </span>
                            <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                              {session.message_count}개 메시지
                            </span>
                          </div>
                          
                          {/* Last Q&A Preview */}
                          {session.last_message_pair.user_message && (
                            <div className="space-y-1">
                              <div className="text-sm">
                                <span className="font-medium text-blue-600">나:</span>
                                <span className="ml-2 text-gray-700">
                                  {formatMessagePreview(session.last_message_pair.user_message)}
                                </span>
                              </div>
                              {session.last_message_pair.assistant_message && (
                                <div className="text-sm">
                                  <span className="font-medium text-green-600">{characterName}:</span>
                                  <span className="ml-2 text-gray-700">
                                    {formatMessagePreview(session.last_message_pair.assistant_message)}
                                  </span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                        
                        {selectedSession === session.session_id && (
                          <ArrowRight className="w-4 h-4 text-blue-600 ml-2 flex-shrink-0" />
                        )}
                      </div>
                    </motion.div>
                  ))}
                  
                  {selectedSession && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      transition={{ duration: 0.2 }}
                    >
                      <Button 
                        className="w-full mt-3"
                        onClick={() => onContinueSession(selectedSession)}
                      >
                        선택한 대화 계속하기
                      </Button>
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>

        {/* No Previous Sessions Message */}
        {!sessionData.data.can_continue && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-center mt-8"
          >
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <MessageCircle className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                첫 번째 대화입니다
              </h3>
              <p className="text-blue-700">
                {characterName}와의 첫 만남을 시작해보세요!
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}