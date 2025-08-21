'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { SessionStartResponse } from '@/lib/api-client'
import { MessageCircle, Plus, Calendar, ArrowRight, Trash2 } from 'lucide-react'

interface SessionContinuationModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionData: SessionStartResponse;
  onContinueSession: (sessionId: string) => void;
  onCreateNew: () => void;
  onDeleteSession?: (sessionId: string) => void;
  characterName: string;
}

export function SessionContinuationModal({ 
  isOpen,
  onClose,
  sessionData, 
  onContinueSession, 
  onCreateNew, 
  onDeleteSession,
  characterName 
}: SessionContinuationModalProps) {
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

  const formatMessagePreview = (message: string, maxLength: number = 40) => {
    return message.length > maxLength 
      ? message.substring(0, maxLength) + '...' 
      : message
  }

  const handleContinue = () => {
    if (selectedSession) {
      onContinueSession(selectedSession)
      onClose()
    }
  }

  const handleCreateNew = () => {
    onCreateNew()
    onClose()
  }

  const handleDeleteSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (onDeleteSession) {
      onDeleteSession(sessionId)
      if (selectedSession === sessionId) {
        setSelectedSession(null)
      }
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">
            {characterName}와의 대화
          </DialogTitle>
          <DialogDescription>
            이전 대화를 계속하거나 새로운 대화를 시작하세요
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Create New Session Card */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card 
              className="border-2 border-green-200 hover:border-green-300 transition-colors cursor-pointer"
              onClick={handleCreateNew}
            >
              <CardHeader className="text-center pb-3">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Plus className="w-6 h-6 text-green-600" />
                </div>
                <CardTitle className="text-green-700 text-lg">새로운 대화 시작</CardTitle>
                <CardDescription>
                  처음부터 새로운 대화를 시작합니다
                </CardDescription>
              </CardHeader>
            </Card>
          </motion.div>

          {/* Previous Sessions */}
          {sessionData.data.can_continue && sessionData.data.previous_sessions.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 pt-2">
                <MessageCircle className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-blue-700">이전 대화 계속하기</h3>
                <span className="text-sm text-gray-500">
                  ({sessionData.data.previous_sessions.length}개 세션)
                </span>
              </div>
              
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {sessionData.data.previous_sessions.map((session, index) => (
                  <motion.div
                    key={session.session_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 + index * 0.05 }}
                    className={`p-3 border rounded-lg cursor-pointer transition-all group ${ 
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
                      
                      <div className="flex items-center gap-2 ml-2">
                        {selectedSession === session.session_id && (
                          <ArrowRight className="w-4 h-4 text-blue-600 flex-shrink-0" />
                        )}
                        {onDeleteSession && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-700 hover:bg-red-50"
                            onClick={(e) => handleDeleteSession(session.session_id, e)}
                            title="세션 삭제"
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
              
              <AnimatePresence>
                {selectedSession && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Button 
                      className="w-full"
                      onClick={handleContinue}
                    >
                      선택한 대화 계속하기
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* No Previous Sessions */}
          {(!sessionData.data.can_continue || sessionData.data.previous_sessions.length === 0) && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-center py-4"
            >
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <MessageCircle className="w-10 h-10 text-blue-600 mx-auto mb-3" />
                <h3 className="text-lg font-semibold text-blue-900 mb-2">
                  첫 번째 대화입니다
                </h3>
                <p className="text-blue-700 text-sm">
                  {characterName}와의 첫 만남을 시작해보세요!
                </p>
              </div>
            </motion.div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}