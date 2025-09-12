'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Character } from '@/types/character'
import PlatformChatInterface from '@/components/PlatformChatInterface'
import { ArrowLeft } from 'lucide-react'
import { useRouter } from 'next/navigation'

export default function PlatformTestPage() {
  const router = useRouter()
  
  // Test character for platform integration
  const testCharacter: Character = {
    id: 'seolminseok_korean_history_chat',
    name: '설민석 AI 퀴즈 튜터',
    description: '한국사 전문 AI 튜터',
    prompt: 'You are 설민석, a Korean history teacher.',
    voice_id: 'seol_voice',
    image: '/images/seol_character.png',
    greetings: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  return (
    <div className="flex h-screen flex-col bg-gradient-to-b from-slate-50 to-slate-100/40">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-slate-50/95 backdrop-blur supports-[backdrop-filter]:bg-slate-50/60">
        <div className="container flex h-16 max-w-2xl mx-auto items-center justify-between px-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/characters')}
            className="h-9 w-9 rounded-full p-0"
          >
            <ArrowLeft className="h-4 w-4" />
            <span className="sr-only">뒤로 가기</span>
          </Button>
          
          <div className="flex flex-1 flex-col items-center text-center">
            <h1 className="text-lg font-semibold leading-tight">Platform Chat Test</h1>
            <p className="text-sm text-muted-foreground">New Tool-Driven Architecture</p>
          </div>
          
          <div className="w-9" /> {/* Spacer for centering */}
        </div>
      </header>

      {/* Platform chat interface */}
      <div className="flex-1">
        <PlatformChatInterface 
          character={testCharacter}
          userId="platform_test_user"
        />
      </div>
    </div>
  )
}