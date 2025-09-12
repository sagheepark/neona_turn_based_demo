// FRONTEND UI BEHAVIOR TEST SCRIPT
// Paste this into browser console at http://localhost:3000/chat/seol_min_seok_quiz
// This will test the actual UI behavior when quiz is answered

console.log("🧪 FRONTEND UI BEHAVIOR TEST");
console.log("========================================");

// Test function to monitor UI state changes
function testFlowUIBehavior() {
  console.log("🔹 Starting UI behavior monitoring...");
  
  // Monitor messages array changes
  const originalMessages = window.React?._currentOwner?.current?.stateNode?.state?.messages || [];
  console.log(`📝 Initial messages count: ${originalMessages.length}`);
  
  // Monitor tools changes
  const checkUIState = () => {
    const messagesContainer = document.querySelector('[class*="messages"]');
    const toolsContainer = document.querySelector('[class*="tools"], [class*="selection"]');
    const audioElement = document.querySelector('audio');
    
    console.log("🔍 UI STATE CHECK:");
    console.log(`  📝 Messages in DOM: ${messagesContainer?.children?.length || 0}`);
    console.log(`  🔧 Tools/selections visible: ${toolsContainer ? 'YES' : 'NO'}`);
    console.log(`  🎵 Audio element present: ${audioElement ? 'YES' : 'NO'}`);
    console.log(`  🎵 Audio playing: ${audioElement?.paused === false ? 'YES' : 'NO'}`);
    
    // Check for thinking indicator
    const thinkingIndicator = document.querySelector('[class*="thinking"], [class*="loading"]');
    console.log(`  🤔 Thinking indicator: ${thinkingIndicator ? 'YES' : 'NO'}`);
    
    return {
      messagesCount: messagesContainer?.children?.length || 0,
      toolsVisible: !!toolsContainer,
      audioPlaying: audioElement?.paused === false,
      thinkingVisible: !!thinkingIndicator
    };
  };
  
  // Initial state
  const initialState = checkUIState();
  console.log("📊 INITIAL STATE:", initialState);
  
  // Set up monitoring
  let checkCount = 0;
  const maxChecks = 20;
  
  const monitor = setInterval(() => {
    checkCount++;
    console.log(`\n🔍 UI CHECK #${checkCount}:`);
    
    const currentState = checkUIState();
    
    // Compare with initial state
    const changes = {
      messagesAdded: currentState.messagesCount > initialState.messagesCount,
      toolsAppeared: currentState.toolsVisible && !initialState.toolsVisible,
      audioStarted: currentState.audioPlaying && !initialState.audioPlaying
    };
    
    console.log("📈 CHANGES DETECTED:", changes);
    
    // Stop monitoring after max checks or when we see all expected changes
    if (checkCount >= maxChecks || (changes.messagesAdded && changes.toolsAppeared)) {
      clearInterval(monitor);
      
      console.log("\n🎯 FINAL UI BEHAVIOR ANALYSIS:");
      console.log("========================================");
      console.log(`✅ Text message appeared: ${changes.messagesAdded ? 'YES' : 'NO'}`);
      console.log(`✅ Next quiz tools appeared: ${changes.toolsAppeared ? 'YES' : 'NO'}`);  
      console.log(`✅ Audio started playing: ${changes.audioStarted ? 'YES' : 'NO'}`);
      
      if (changes.messagesAdded && changes.toolsAppeared) {
        console.log("\n🎉 SUCCESS: UI behavior working as expected!");
      } else {
        console.log("\n❌ FAILURE: UI not displaying flow results correctly");
        console.log("   This confirms the original issue is NOT fully fixed");
      }
    }
  }, 500); // Check every 500ms
  
  console.log("📱 Now click on a quiz answer in the UI to test...");
  console.log("   Monitoring will run for 10 seconds or until changes detected");
}

// Instructions for user
console.log("\n📋 INSTRUCTIONS:");
console.log("1. Make sure you're on http://localhost:3000/chat/seol_min_seok_quiz");
console.log("2. Send '조선시대 퀴즈' to get quiz options");
console.log("3. Run: testFlowUIBehavior()");
console.log("4. Click on a quiz answer");
console.log("5. Watch the console for UI behavior analysis");

console.log("\n🚀 Ready to test! Run: testFlowUIBehavior()");