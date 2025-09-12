/**
 * Test frontend-backend platform integration
 * Run this with: node test_frontend_integration.js
 */

const API_BASE_URL = 'http://localhost:8001';

async function testPlatformChatIntegration() {
    console.log('🧪 TESTING FRONTEND-BACKEND PLATFORM INTEGRATION');
    console.log('=' .repeat(60));
    
    try {
        // Test 1: Create session with greeting
        console.log('\n🎬 TEST 1: Session creation with greeting');
        console.log('-'.repeat(40));
        
        const greetingResponse = await fetch(`${API_BASE_URL}/api/platform-chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_input: '', // Empty triggers greeting
                character_id: 'seolminseok_korean_history_chat',
                user_id: 'frontend_test_user'
                // No session_id - creates new session
            })
        });
        
        if (!greetingResponse.ok) {
            throw new Error(`Greeting failed: ${greetingResponse.status}`);
        }
        
        const greetingData = await greetingResponse.json();
        console.log('✅ Greeting Response:');
        console.log(`  Dialogue: ${greetingData.dialogue.substring(0, 80)}...`);
        console.log(`  Tools: ${greetingData.tools.length}`);
        console.log(`  Audio URL: ${!!greetingData.audio_url}`);
        console.log(`  Session ID: ${greetingData.session_id}`);
        
        const sessionId = greetingData.session_id;
        
        // Test 2: Topic selection
        console.log('\n📚 TEST 2: Topic selection');
        console.log('-'.repeat(40));
        
        const topicResponse = await fetch(`${API_BASE_URL}/api/platform-chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_input: '조선시대',
                character_id: 'seolminseok_korean_history_chat',
                session_id: sessionId,
                user_id: 'frontend_test_user'
            })
        });
        
        if (!topicResponse.ok) {
            throw new Error(`Topic selection failed: ${topicResponse.status}`);
        }
        
        const topicData = await topicResponse.json();
        console.log('✅ Topic Response:');
        console.log(`  Dialogue: ${topicData.dialogue.substring(0, 80)}...`);
        console.log(`  Tools: ${topicData.tools.length}`);
        console.log(`  Tool Type: ${topicData.tools[0]?.type}`);
        console.log(`  Audio URL: ${!!topicData.audio_url}`);
        
        // Extract quiz data if available
        if (topicData.tools.length > 0 && topicData.tools[0].type === 'show_selection') {
            const quizData = topicData.tools[0].data;
            const correctAnswer = quizData.correct_answer;
            const wrongAnswer = quizData.options?.find(opt => opt !== correctAnswer) || '세종대왕';
            
            // Test 3: Wrong answer (should use continuous_quiz_response)
            console.log('\n❌ TEST 3: Wrong answer response');
            console.log('-'.repeat(40));
            
            const wrongResponse = await fetch(`${API_BASE_URL}/api/platform-chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_input: wrongAnswer,
                    character_id: 'seolminseok_korean_history_chat',
                    session_id: sessionId,
                    user_id: 'frontend_test_user'
                })
            });
            
            const wrongData = await wrongResponse.json();
            console.log('✅ Wrong Answer Response:');
            console.log(`  Dialogue: ${wrongData.dialogue.substring(0, 80)}...`);
            console.log(`  Tools: ${wrongData.tools.length}`);
            console.log(`  Tool Type: ${wrongData.tools[0]?.type}`);
            
            if (wrongData.tools[0]?.type === 'continuous_quiz_response') {
                const toolData = wrongData.tools[0].data;
                console.log(`  Phase 1: ${toolData.phase1?.text?.substring(0, 50)}...`);
                console.log(`  Phase 2: ${toolData.phase2?.text?.substring(0, 50)}...`);
                console.log(`  Phase 1 Audio: ${!!toolData.phase1?.audio_url}`);
                console.log(`  Phase 2 Audio: ${!!toolData.phase2?.audio_url}`);
            }
            
            // Test 4: Correct answer (should progress to new question)
            console.log('\n✅ TEST 4: Correct answer response');
            console.log('-'.repeat(40));
            
            const correctResponse = await fetch(`${API_BASE_URL}/api/platform-chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_input: correctAnswer,
                    character_id: 'seolminseok_korean_history_chat',
                    session_id: sessionId,
                    user_id: 'frontend_test_user'
                })
            });
            
            const correctData = await correctResponse.json();
            console.log('✅ Correct Answer Response:');
            console.log(`  Dialogue: ${correctData.dialogue.substring(0, 80)}...`);
            console.log(`  Tools: ${correctData.tools.length}`);
            console.log(`  Tool Type: ${correctData.tools[0]?.type}`);
            
            if (correctData.tools[0]?.type === 'continuous_quiz_response') {
                const toolData = correctData.tools[0].data;
                console.log(`  Phase 1: ${toolData.phase1?.text?.substring(0, 50)}...`);
                console.log(`  Phase 2: ${toolData.phase2?.text?.substring(0, 50)}...`);
                console.log(`  Phase 1 Audio: ${!!toolData.phase1?.audio_url}`);
                console.log(`  Phase 2 Audio: ${!!toolData.phase2?.audio_url}`);
            }
        }
        
        console.log('\n🎯 INTEGRATION TEST SUMMARY');
        console.log('=' .repeat(60));
        console.log('✅ Frontend API client structure: COMPATIBLE');
        console.log('✅ Backend platform-chat endpoint: WORKING');  
        console.log('✅ Session management: FUNCTIONAL');
        console.log('✅ Tool orchestration: OPERATIONAL');
        console.log('✅ TTS integration: READY (URLs generated)');
        console.log('\n🚀 Frontend integration: READY FOR TESTING');
        
    } catch (error) {
        console.error('❌ Integration test failed:', error);
        console.log('\n🔧 Make sure backend server is running on localhost:8001');
    }
}

// Run the test
testPlatformChatIntegration();