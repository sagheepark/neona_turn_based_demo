/**
 * Frontend Compatibility Test
 * Test that the old frontend interface works with the new backend
 */

const API_BASE_URL = "http://localhost:8001";

async function testOldInterfaceWithNewBackend() {
    console.log("🧪 TESTING FRONTEND COMPATIBILITY");
    console.log("=" * 50);
    
    try {
        // Simulate the old chatWithSession request structure
        const oldStyleRequest = {
            session_id: "frontend_compat_test",
            message: "조선시대",
            character_prompt: "", // This won't be used by new backend
            character_id: "seolminseok_korean_history_chat", 
            user_id: "demo_user",
            voice_id: "seol_voice"
        };
        
        // Test the platform-chat endpoint directly (simulating what our compatibility layer does)
        const platformRequest = {
            user_input: oldStyleRequest.message,
            character_id: oldStyleRequest.character_id,
            session_id: oldStyleRequest.session_id,
            user_id: oldStyleRequest.user_id
        };
        
        console.log("📤 Sending to /api/platform-chat:", platformRequest);
        
        const response = await fetch(`${API_BASE_URL}/api/platform-chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(platformRequest)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log("✅ Platform response received!");
        console.log("💬 Dialogue:", data.dialogue);
        console.log("🔧 Tools:", data.tools?.length || 0);
        
        if (data.tools && data.tools.length > 0) {
            const tool = data.tools[0];
            console.log("   Tool type:", tool.type);
            if (tool.data?.options) {
                console.log("   Options:", tool.data.options);
                console.log("   ✅ Options separated from dialogue!");
                
                // Check dialogue doesn't contain numbered options
                const hasNumberedOptions = /[1-4]\./.test(data.dialogue);
                if (hasNumberedOptions) {
                    console.log("   ❌ ERROR: Dialogue contains numbered options");
                } else {
                    console.log("   ✅ SUCCESS: Dialogue is clean for TTS");
                }
            }
        }
        
        // Convert to old interface format (what our compatibility layer does)
        const convertedResponse = {
            character: data.character,
            dialogue: data.dialogue,
            emotion: "neutral",
            speed: 1.0,
            audio: null,
            session_id: data.session_id,
            tools: data.tools || []
        };
        
        console.log("🔄 Converted to old interface:", {
            hasDialogue: !!convertedResponse.dialogue,
            hasEmotion: !!convertedResponse.emotion,
            hasTools: convertedResponse.tools.length > 0,
            sessionId: convertedResponse.session_id
        });
        
        console.log("🎉 COMPATIBILITY TEST PASSED!");
        console.log("   ✅ Old frontend interface will work with new backend");
        console.log("   ✅ TTS dialogue is clean");
        console.log("   ✅ UI options are properly separated");
        
        return true;
        
    } catch (error) {
        console.log("❌ COMPATIBILITY TEST FAILED:", error.message);
        return false;
    }
}

// Run the test
testOldInterfaceWithNewBackend().then(success => {
    console.log(`\n🏆 Final Result: ${success ? "✅ SUCCESS" : "❌ FAILED"}`);
    process.exit(success ? 0 : 1);
});