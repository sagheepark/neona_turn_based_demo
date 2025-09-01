import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np

# Set up the style
plt.style.use('default')

def create_high_level_architecture():
    """Create high-level system architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define colors
    colors = {
        'frontend': '#4A90E2',
        'api': '#F39C12',
        'orchestrator': '#E74C3C',
        'services': '#27AE60',
        'storage': '#8E44AD',
        'ai': '#16A085'
    }
    
    # Frontend Layer
    frontend_rect = FancyBboxPatch((0.5, 8), 9, 1.2, 
                                   boxstyle="round,pad=0.1",
                                   facecolor=colors['frontend'], 
                                   edgecolor='black', 
                                   alpha=0.7)
    ax.add_patch(frontend_rect)
    ax.text(5, 8.6, 'Frontend Layer', fontsize=14, fontweight='bold', ha='center', color='white')
    ax.text(2, 8.3, 'Next.js UI', fontsize=10, ha='center', color='white')
    ax.text(5, 8.3, 'Voice Input (STT)', fontsize=10, ha='center', color='white')
    ax.text(8, 8.3, 'Text Input', fontsize=10, ha='center', color='white')
    
    # API Gateway
    api_rect = FancyBboxPatch((2, 6.5), 6, 0.8,
                              boxstyle="round,pad=0.1",
                              facecolor=colors['api'],
                              edgecolor='black',
                              alpha=0.7)
    ax.add_patch(api_rect)
    ax.text(5, 6.9, 'API Gateway - FastAPI Server', fontsize=12, fontweight='bold', ha='center', color='white')
    
    # Orchestration Layer
    orch_rect = FancyBboxPatch((2.5, 5.2), 5, 0.8,
                               boxstyle="round,pad=0.1",
                               facecolor=colors['orchestrator'],
                               edgecolor='black',
                               alpha=0.7)
    ax.add_patch(orch_rect)
    ax.text(5, 5.6, 'Chat Orchestrator', fontsize=12, fontweight='bold', ha='center', color='white')
    
    # Core Services
    services_rect = FancyBboxPatch((0.5, 3), 9, 1.5,
                                   boxstyle="round,pad=0.1",
                                   facecolor=colors['services'],
                                   edgecolor='black',
                                   alpha=0.7)
    ax.add_patch(services_rect)
    ax.text(5, 4.2, 'Core Services', fontsize=12, fontweight='bold', ha='center', color='white')
    
    # Individual services
    service_names = ['Knowledge\nService', 'Memory\nService', 'Conversation\nService', 'Persona\nService']
    service_positions = [2, 4, 6, 8]
    for name, pos in zip(service_names, service_positions):
        service_box = FancyBboxPatch((pos-0.7, 3.2), 1.4, 0.7,
                                     boxstyle="round,pad=0.05",
                                     facecolor='white',
                                     edgecolor='black',
                                     alpha=0.9)
        ax.add_patch(service_box)
        ax.text(pos, 3.55, name, fontsize=9, ha='center', va='center')
    
    # Storage Layer
    storage_rect = FancyBboxPatch((0.5, 1), 9, 1.5,
                                  boxstyle="round,pad=0.1",
                                  facecolor=colors['storage'],
                                  edgecolor='black',
                                  alpha=0.7)
    ax.add_patch(storage_rect)
    ax.text(5, 2.2, 'Storage Layer', fontsize=12, fontweight='bold', ha='center', color='white')
    
    # Storage components
    storage_names = ['MongoDB', 'File System', 'In-Memory\nCache']
    storage_positions = [2.5, 5, 7.5]
    for name, pos in zip(storage_names, storage_positions):
        storage_box = FancyBboxPatch((pos-0.7, 1.2), 1.4, 0.7,
                                     boxstyle="round,pad=0.05",
                                     facecolor='white',
                                     edgecolor='black',
                                     alpha=0.9)
        ax.add_patch(storage_box)
        ax.text(pos, 1.55, name, fontsize=9, ha='center', va='center')
    
    # AI Services (right side)
    ai_rect = FancyBboxPatch((10.2, 3), 2.5, 3,
                             boxstyle="round,pad=0.1",
                             facecolor=colors['ai'],
                             edgecolor='black',
                             alpha=0.7)
    ax.add_patch(ai_rect)
    ax.text(11.45, 5.5, 'AI Services', fontsize=12, fontweight='bold', ha='center', color='white')
    
    ai_services = ['Azure\nOpenAI\nGPT-4', 'Azure\nTTS', 'Azure\nSTT']
    ai_positions = [5, 4, 3]
    for name, pos in zip(ai_services, ai_positions):
        ai_box = FancyBboxPatch((10.4, pos-0.35), 2.1, 0.7,
                                boxstyle="round,pad=0.05",
                                facecolor='white',
                                edgecolor='black',
                                alpha=0.9)
        ax.add_patch(ai_box)
        ax.text(11.45, pos, name, fontsize=9, ha='center', va='center')
    
    # Add arrows for data flow
    # Frontend to API
    arrow1 = FancyArrowPatch((5, 8), (5, 7.3),
                            connectionstyle="arc3",
                            arrowstyle='->,head_width=0.3,head_length=0.3',
                            color='black', linewidth=2)
    ax.add_patch(arrow1)
    
    # API to Orchestrator
    arrow2 = FancyArrowPatch((5, 6.5), (5, 6),
                            connectionstyle="arc3",
                            arrowstyle='->,head_width=0.3,head_length=0.3',
                            color='black', linewidth=2)
    ax.add_patch(arrow2)
    
    # Orchestrator to Services
    arrow3 = FancyArrowPatch((5, 5.2), (5, 4.5),
                            connectionstyle="arc3",
                            arrowstyle='->,head_width=0.3,head_length=0.3',
                            color='black', linewidth=2)
    ax.add_patch(arrow3)
    
    # Services to Storage
    arrow4 = FancyArrowPatch((5, 3), (5, 2.5),
                            connectionstyle="arc3",
                            arrowstyle='->,head_width=0.3,head_length=0.3',
                            color='black', linewidth=2)
    ax.add_patch(arrow4)
    
    # Orchestrator to AI Services
    arrow5 = FancyArrowPatch((7.5, 5.6), (10.2, 4.5),
                            connectionstyle="arc3,rad=0.3",
                            arrowstyle='->,head_width=0.3,head_length=0.3',
                            color='black', linewidth=2)
    ax.add_patch(arrow5)
    
    # Extend the axes to show AI services
    ax.set_xlim(0, 13)
    
    plt.title('Voice Character Chat - High-Level Architecture', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/Users/bagsanghui/neona_turn_based_demo_with_agent/documents/architecture_high_level.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_rag_system_diagram():
    """Create RAG system architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'RAG (Retrieval-Augmented Generation) System', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Knowledge Input
    input_rect = FancyBboxPatch((0.5, 7), 3, 1.5,
                                boxstyle="round,pad=0.1",
                                facecolor='#3498DB',
                                edgecolor='black',
                                alpha=0.7)
    ax.add_patch(input_rect)
    ax.text(2, 8.2, 'Knowledge Input', fontsize=11, fontweight='bold', ha='center', color='white')
    ax.text(2, 7.7, '• Knowledge Items', fontsize=9, ha='center', color='white')
    ax.text(2, 7.4, '• Keywords/Tags', fontsize=9, ha='center', color='white')
    ax.text(2, 7.1, '• Categories', fontsize=9, ha='center', color='white')
    
    # Storage
    storage_rect = FancyBboxPatch((5, 7), 3, 1.5,
                                 boxstyle="round,pad=0.1",
                                 facecolor='#9B59B6',
                                 edgecolor='black',
                                 alpha=0.7)
    ax.add_patch(storage_rect)
    ax.text(6.5, 8.2, 'Knowledge Storage', fontsize=11, fontweight='bold', ha='center', color='white')
    ax.text(6.5, 7.7, '• JSON Files', fontsize=9, ha='center', color='white')
    ax.text(6.5, 7.4, '• In-Memory Cache', fontsize=9, ha='center', color='white')
    ax.text(6.5, 7.1, '• Session Cache', fontsize=9, ha='center', color='white')
    
    # Three-tier Knowledge Services
    services_rect = FancyBboxPatch((0.5, 4.5), 7.5, 2,
                                   boxstyle="round,pad=0.1",
                                   facecolor='#27AE60',
                                   edgecolor='black',
                                   alpha=0.7)
    ax.add_patch(services_rect)
    ax.text(4.25, 6.2, 'Three-Tier Knowledge Services', fontsize=12, fontweight='bold', ha='center', color='white')
    
    # Individual service boxes
    # Base Knowledge Service
    base_box = FancyBboxPatch((1, 4.8), 2, 1.2,
                              boxstyle="round,pad=0.05",
                              facecolor='white',
                              edgecolor='black',
                              alpha=0.9)
    ax.add_patch(base_box)
    ax.text(2, 5.7, 'Base Knowledge', fontsize=9, fontweight='bold', ha='center')
    ax.text(2, 5.4, 'Service', fontsize=9, fontweight='bold', ha='center')
    ax.text(2, 5.1, '• CRUD Operations', fontsize=7, ha='center')
    ax.text(2, 4.9, '• Basic Search', fontsize=7, ha='center')
    
    # Enhanced Knowledge Service
    enhanced_box = FancyBboxPatch((3.5, 4.8), 2, 1.2,
                                  boxstyle="round,pad=0.05",
                                  facecolor='white',
                                  edgecolor='black',
                                  alpha=0.9)
    ax.add_patch(enhanced_box)
    ax.text(4.5, 5.7, 'Enhanced Knowledge', fontsize=9, fontweight='bold', ha='center')
    ax.text(4.5, 5.4, 'Service', fontsize=9, fontweight='bold', ha='center')
    ax.text(4.5, 5.1, '• Semantic Expansion', fontsize=7, ha='center')
    ax.text(4.5, 4.9, '• Smart Search', fontsize=7, ha='center')
    
    # Incremental Cache
    cache_box = FancyBboxPatch((6, 4.8), 2, 1.2,
                               boxstyle="round,pad=0.05",
                               facecolor='white',
                               edgecolor='black',
                               alpha=0.9)
    ax.add_patch(cache_box)
    ax.text(7, 5.7, 'Incremental', fontsize=9, fontweight='bold', ha='center')
    ax.text(7, 5.4, 'Knowledge Cache', fontsize=9, fontweight='bold', ha='center')
    ax.text(7, 5.1, '• Session Caching', fontsize=7, ha='center')
    ax.text(7, 4.9, '• Topic Extraction', fontsize=7, ha='center')
    
    # Retrieval System
    retrieval_rect = FancyBboxPatch((9, 4.5), 4.5, 2,
                                    boxstyle="round,pad=0.1",
                                    facecolor='#E67E22',
                                    edgecolor='black',
                                    alpha=0.7)
    ax.add_patch(retrieval_rect)
    ax.text(11.25, 6.2, 'Retrieval System', fontsize=12, fontweight='bold', ha='center', color='white')
    
    # Retrieval components
    components = [
        ('Query Processor', 11.25, 5.7),
        ('Topic Extractor', 11.25, 5.3),
        ('Relevance Scorer', 11.25, 4.9)
    ]
    for name, x, y in components:
        comp_box = FancyBboxPatch((x-1.5, y-0.15), 3, 0.3,
                                  boxstyle="round,pad=0.02",
                                  facecolor='white',
                                  edgecolor='black',
                                  alpha=0.9)
        ax.add_patch(comp_box)
        ax.text(x, y, name, fontsize=8, ha='center', va='center')
    
    # Scoring Weights Box
    weights_rect = FancyBboxPatch((0.5, 2), 5, 2,
                                 boxstyle="round,pad=0.1",
                                 facecolor='#F39C12',
                                 edgecolor='black',
                                 alpha=0.7)
    ax.add_patch(weights_rect)
    ax.text(3, 3.7, 'Weighted Scoring System', fontsize=11, fontweight='bold', ha='center')
    ax.text(3, 3.3, 'Trigger Keywords: 10 points', fontsize=9, ha='center')
    ax.text(3, 3.0, 'Title Match: 5 points', fontsize=9, ha='center')
    ax.text(3, 2.7, 'Tag Match: 3 points', fontsize=9, ha='center')
    ax.text(3, 2.4, 'Content Match: 1 point', fontsize=9, ha='center')
    
    # Topic Relevance Box
    relevance_rect = FancyBboxPatch((6, 2), 5, 2,
                                    boxstyle="round,pad=0.1",
                                    facecolor='#16A085',
                                    edgecolor='black',
                                    alpha=0.7)
    ax.add_patch(relevance_rect)
    ax.text(8.5, 3.7, 'Topic Relevance Scoring', fontsize=11, fontweight='bold', ha='center', color='white')
    ax.text(8.5, 3.3, 'Direct Match: 0.8 score', fontsize=9, ha='center', color='white')
    ax.text(8.5, 3.0, 'Substring Match: 0.6 score', fontsize=9, ha='center', color='white')
    ax.text(8.5, 2.7, 'Related Topics: 0.3 score', fontsize=9, ha='center', color='white')
    ax.text(8.5, 2.4, 'Temporal Keywords: 0.2 score', fontsize=9, ha='center', color='white')
    
    # Data Structure Example
    data_rect = FancyBboxPatch((11.5, 2), 2, 2,
                              boxstyle="round,pad=0.1",
                              facecolor='#34495E',
                              edgecolor='black',
                              alpha=0.7)
    ax.add_patch(data_rect)
    ax.text(12.5, 3.7, 'Knowledge Item', fontsize=10, fontweight='bold', ha='center', color='white')
    ax.text(12.5, 3.4, 'id: kb_xxxxx', fontsize=7, ha='center', color='white')
    ax.text(12.5, 3.2, 'title: string', fontsize=7, ha='center', color='white')
    ax.text(12.5, 3.0, 'content: string', fontsize=7, ha='center', color='white')
    ax.text(12.5, 2.8, 'keywords: []', fontsize=7, ha='center', color='white')
    ax.text(12.5, 2.6, 'category: string', fontsize=7, ha='center', color='white')
    ax.text(12.5, 2.4, 'usage_count: int', fontsize=7, ha='center', color='white')
    
    # Add flow arrows
    # Input to Storage
    arrow1 = FancyArrowPatch((3.5, 7.75), (5, 7.75),
                            arrowstyle='->,head_width=0.2,head_length=0.2',
                            color='black', linewidth=1.5)
    ax.add_patch(arrow1)
    
    # Storage to Services
    arrow2 = FancyArrowPatch((6.5, 7), (4.25, 6.5),
                            connectionstyle="arc3,rad=0.3",
                            arrowstyle='->,head_width=0.2,head_length=0.2',
                            color='black', linewidth=1.5)
    ax.add_patch(arrow2)
    
    # Services to Retrieval
    arrow3 = FancyArrowPatch((8, 5.5), (9, 5.5),
                            arrowstyle='->,head_width=0.2,head_length=0.2',
                            color='black', linewidth=1.5)
    ax.add_patch(arrow3)
    
    # Retrieval to Output
    arrow4 = FancyArrowPatch((11.25, 4.5), (11.25, 0.5),
                            arrowstyle='->,head_width=0.2,head_length=0.2',
                            color='black', linewidth=1.5)
    ax.add_patch(arrow4)
    
    # Output label
    ax.text(11.25, 0.3, 'Retrieved Knowledge', fontsize=10, fontweight='bold', ha='center')
    
    plt.tight_layout()
    plt.savefig('/Users/bagsanghui/neona_turn_based_demo_with_agent/documents/architecture_rag_system.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_memory_system_diagram():
    """Create Memory System architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'Selective Memory System Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Core Memory Structure
    memory_rect = FancyBboxPatch((0.5, 6.5), 6, 2.5,
                                 boxstyle="round,pad=0.1",
                                 facecolor='#8E44AD',
                                 edgecolor='black',
                                 alpha=0.7)
    ax.add_patch(memory_rect)
    ax.text(3.5, 8.7, 'Core Memory Structure', fontsize=12, fontweight='bold', ha='center', color='white')
    
    # Memory components
    components = [
        ('Status Values', 2, 8.2, 'Dynamic metrics\n(affection, trust, stress)'),
        ('Milestones', 5, 8.2, 'Achievements\n& rewards'),
        ('Event Log', 2, 7.4, 'Timestamped\nevents (max 100)'),
        ('Persistent Facts', 5, 7.4, 'User info\n(max 50)'),
        ('Compressed History', 3.5, 6.8, 'Summarized conversations')
    ]
    
    for name, x, y, desc in components:
        comp_box = FancyBboxPatch((x-0.8, y-0.25), 1.6, 0.5,
                                  boxstyle="round,pad=0.02",
                                  facecolor='white',
                                  edgecolor='black',
                                  alpha=0.9)
        ax.add_patch(comp_box)
        ax.text(x, y+0.1, name, fontsize=8, fontweight='bold', ha='center')
        ax.text(x, y-0.1, desc, fontsize=6, ha='center', style='italic')
    
    # Memory Operations
    ops_rect = FancyBboxPatch((7.5, 6.5), 6, 2.5,
                              boxstyle="round,pad=0.1",
                              facecolor='#E74C3C',
                              edgecolor='black',
                              alpha=0.7)
    ax.add_patch(ops_rect)
    ax.text(10.5, 8.7, 'Memory Operations', fontsize=12, fontweight='bold', ha='center', color='white')
    
    # Operations
    operations = [
        ('Initialize Memory', 9, 8.2),
        ('Update Status', 12, 8.2),
        ('Check Milestones', 9, 7.6),
        ('Log Events', 12, 7.6),
        ('Compress History', 10.5, 7.0)
    ]
    
    for name, x, y in operations:
        op_box = FancyBboxPatch((x-0.9, y-0.15), 1.8, 0.3,
                                boxstyle="round,pad=0.02",
                                facecolor='white',
                                edgecolor='black',
                                alpha=0.9)
        ax.add_patch(op_box)
        ax.text(x, y, name, fontsize=8, ha='center', va='center')
    
    # Milestone System
    milestone_rect = FancyBboxPatch((0.5, 4), 6, 2,
                                    boxstyle="round,pad=0.1",
                                    facecolor='#27AE60',
                                    edgecolor='black',
                                    alpha=0.7)
    ax.add_patch(milestone_rect)
    ax.text(3.5, 5.7, 'Milestone System', fontsize=11, fontweight='bold', ha='center', color='white')
    
    # Milestone conditions
    ax.text(3.5, 5.3, 'Condition Triggers:', fontsize=9, fontweight='bold', ha='center', color='white')
    ax.text(3.5, 5.0, '• Conversation count thresholds', fontsize=8, ha='center', color='white')
    ax.text(3.5, 4.7, '• Status value thresholds', fontsize=8, ha='center', color='white')
    ax.text(3.5, 4.4, '• Event type counts', fontsize=8, ha='center', color='white')
    ax.text(3.5, 4.1, '• Context conditions', fontsize=8, ha='center', color='white')
    
    # Configuration System
    config_rect = FancyBboxPatch((7.5, 4), 6, 2,
                                boxstyle="round,pad=0.1",
                                facecolor='#F39C12',
                                edgecolor='black',
                                alpha=0.7)
    ax.add_patch(config_rect)
    ax.text(10.5, 5.7, 'Configuration System', fontsize=11, fontweight='bold', ha='center')
    
    # Config components
    ax.text(10.5, 5.3, 'Character Config Parser', fontsize=9, fontweight='bold', ha='center')
    ax.text(10.5, 5.0, '• Status definitions', fontsize=8, ha='center')
    ax.text(10.5, 4.7, '• Milestone definitions', fontsize=8, ha='center')
    ax.text(10.5, 4.4, '• Event triggers', fontsize=8, ha='center')
    ax.text(10.5, 4.1, '• Compression prompts', fontsize=8, ha='center')
    
    # Storage
    storage_rect = FancyBboxPatch((2, 1.5), 10, 1.5,
                                  boxstyle="round,pad=0.1",
                                  facecolor='#34495E',
                                  edgecolor='black',
                                  alpha=0.7)
    ax.add_patch(storage_rect)
    ax.text(7, 2.7, 'Storage Layer', fontsize=11, fontweight='bold', ha='center', color='white')
    
    # Storage components
    mongo_box = FancyBboxPatch((3, 1.8), 3, 0.8,
                               boxstyle="round,pad=0.02",
                               facecolor='white',
                               edgecolor='black',
                               alpha=0.9)
    ax.add_patch(mongo_box)
    ax.text(4.5, 2.2, 'MongoDB', fontsize=9, fontweight='bold', ha='center')
    ax.text(4.5, 1.95, 'selective_memories', fontsize=7, ha='center', style='italic')
    
    cache_box = FancyBboxPatch((8, 1.8), 3, 0.8,
                               boxstyle="round,pad=0.02",
                               facecolor='white',
                               edgecolor='black',
                               alpha=0.9)
    ax.add_patch(cache_box)
    ax.text(9.5, 2.2, 'Memory Cache', fontsize=9, fontweight='bold', ha='center')
    ax.text(9.5, 1.95, '{user_id}_{character_id}', fontsize=7, ha='center', style='italic')
    
    # Add flow arrows
    # Memory to Operations
    arrow1 = FancyArrowPatch((6.5, 7.75), (7.5, 7.75),
                            arrowstyle='<->,head_width=0.2,head_length=0.2',
                            color='black', linewidth=1.5)
    ax.add_patch(arrow1)
    
    # Operations to Storage
    arrow2 = FancyArrowPatch((10.5, 6.5), (7, 3),
                            connectionstyle="arc3,rad=0.3",
                            arrowstyle='->,head_width=0.2,head_length=0.2',
                            color='black', linewidth=1.5)
    ax.add_patch(arrow2)
    
    # Memory to Storage
    arrow3 = FancyArrowPatch((3.5, 6.5), (4.5, 3),
                            connectionstyle="arc3,rad=-0.3",
                            arrowstyle='->,head_width=0.2,head_length=0.2',
                            color='black', linewidth=1.5)
    ax.add_patch(arrow3)
    
    # Config to Operations
    arrow4 = FancyArrowPatch((10.5, 6), (10.5, 6.5),
                            arrowstyle='->,head_width=0.2,head_length=0.2',
                            color='black', linewidth=1.5)
    ax.add_patch(arrow4)
    
    plt.tight_layout()
    plt.savefig('/Users/bagsanghui/neona_turn_based_demo_with_agent/documents/architecture_memory_system.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_message_flow_diagram():
    """Create message processing flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(8, 9.5, 'Complete Message Processing Pipeline', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Define the flow stages
    stages = [
        # Stage 1: Input
        {
            'title': '1. Input Reception',
            'color': '#3498DB',
            'x': 2, 'y': 8, 'w': 3, 'h': 1.2,
            'items': ['Voice → STT', 'Text Input', 'Normalization']
        },
        # Stage 2: Context
        {
            'title': '2. Context Preparation',
            'color': '#9B59B6',
            'x': 6, 'y': 8, 'w': 3, 'h': 1.2,
            'items': ['Load Session', 'Retrieve Knowledge', 'Load Memory']
        },
        # Stage 3: Prompt
        {
            'title': '3. Prompt Construction',
            'color': '#E74C3C',
            'x': 10, 'y': 8, 'w': 3, 'h': 1.2,
            'items': ['Character Prompt', 'Memory Context', 'Knowledge Context']
        },
        # Stage 4: LLM
        {
            'title': '4. LLM Processing',
            'color': '#16A085',
            'x': 14, 'y': 8, 'w': 2, 'h': 1.2,
            'items': ['Azure GPT-4', 'Generate', 'Response']
        },
        # Stage 5: Post-Process
        {
            'title': '5. Post-Processing',
            'color': '#F39C12',
            'x': 14, 'y': 5, 'w': 2, 'h': 1.2,
            'items': ['Update Status', 'Check Milestones', 'Log Events']
        },
        # Stage 6: Memory Update
        {
            'title': '6. Memory Update',
            'color': '#27AE60',
            'x': 10, 'y': 5, 'w': 3, 'h': 1.2,
            'items': ['Add Facts', 'Compress History', 'Save Memory']
        },
        # Stage 7: Response
        {
            'title': '7. Response Delivery',
            'color': '#E67E22',
            'x': 6, 'y': 5, 'w': 3, 'h': 1.2,
            'items': ['TTS Generation', 'Format Response', 'Cache Updates']
        },
        # Stage 8: Output
        {
            'title': '8. Output',
            'color': '#34495E',
            'x': 2, 'y': 5, 'w': 3, 'h': 1.2,
            'items': ['Audio Playback', 'Text Display', 'Session Save']
        }
    ]
    
    # Draw stages
    for stage in stages:
        # Draw box
        box = FancyBboxPatch((stage['x']-stage['w']/2, stage['y']-stage['h']/2), 
                             stage['w'], stage['h'],
                             boxstyle="round,pad=0.1",
                             facecolor=stage['color'],
                             edgecolor='black',
                             alpha=0.7)
        ax.add_patch(box)
        
        # Add title
        ax.text(stage['x'], stage['y']+0.4, stage['title'], 
                fontsize=10, fontweight='bold', ha='center', color='white')
        
        # Add items
        for i, item in enumerate(stage['items']):
            ax.text(stage['x'], stage['y']-0.1-i*0.2, item, 
                   fontsize=8, ha='center', color='white')
    
    # Add flow arrows
    # Top row: 1 -> 2 -> 3 -> 4
    for i in range(3):
        arrow = FancyArrowPatch((2+i*4+1.5, 8), (2+(i+1)*4-1.5, 8),
                               arrowstyle='->,head_width=0.2,head_length=0.2',
                               color='black', linewidth=2)
        ax.add_patch(arrow)
    
    # 4 -> 5 (down)
    arrow = FancyArrowPatch((14, 7.4), (14, 6.2),
                           arrowstyle='->,head_width=0.2,head_length=0.2',
                           color='black', linewidth=2)
    ax.add_patch(arrow)
    
    # Bottom row: 5 -> 6 -> 7 -> 8
    for i in range(3):
        arrow = FancyArrowPatch((14-i*4-1, 5), (14-(i+1)*4+1, 5),
                               arrowstyle='->,head_width=0.2,head_length=0.2',
                               color='black', linewidth=2)
        ax.add_patch(arrow)
    
    # Central data flow descriptions
    ax.text(8, 3, 'Data Flow Details', fontsize=12, fontweight='bold', ha='center')
    
    # Flow details
    details_rect = FancyBboxPatch((1, 0.5), 14, 2,
                                  boxstyle="round,pad=0.1",
                                  facecolor='#ECF0F1',
                                  edgecolor='black',
                                  alpha=0.7)
    ax.add_patch(details_rect)
    
    # Add detail text
    detail_text = [
        'Session Data: session_id, user_id, character_id, persona_id, message history',
        'Knowledge Data: relevant items, scores, keywords, categories, usage counts',
        'Memory Data: status values, milestones, events, facts, compressed history',
        'Response Data: text content, audio (base64), status updates, knowledge used'
    ]
    
    for i, text in enumerate(detail_text):
        ax.text(8, 2.2-i*0.3, text, fontsize=8, ha='center')
    
    plt.tight_layout()
    plt.savefig('/Users/bagsanghui/neona_turn_based_demo_with_agent/documents/architecture_message_flow.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_cache_architecture_diagram():
    """Create cache architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(6, 9.5, 'Multi-Level Cache Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Cache Layers (vertical stack)
    layers = [
        {'name': 'L1: In-Memory Cache', 'color': '#E74C3C', 'y': 7.5, 'speed': 'Fastest (~1ms)'},
        {'name': 'L2: Session Cache', 'color': '#F39C12', 'y': 6, 'speed': 'Fast (~10ms)'},
        {'name': 'L3: Database Cache', 'color': '#3498DB', 'y': 4.5, 'speed': 'Medium (~50ms)'},
        {'name': 'L4: File System', 'color': '#27AE60', 'y': 3, 'speed': 'Slow (~100ms)'}
    ]
    
    for layer in layers:
        # Draw layer box
        box = FancyBboxPatch((1, layer['y']-0.4), 5, 0.8,
                             boxstyle="round,pad=0.05",
                             facecolor=layer['color'],
                             edgecolor='black',
                             alpha=0.7)
        ax.add_patch(box)
        ax.text(3.5, layer['y'], layer['name'], 
                fontsize=11, fontweight='bold', ha='center', color='white')
        ax.text(5.8, layer['y'], layer['speed'], 
                fontsize=8, ha='left', style='italic')
    
    # Cache Types (right side)
    cache_types_rect = FancyBboxPatch((7, 3), 4.5, 5,
                                      boxstyle="round,pad=0.1",
                                      facecolor='#9B59B6',
                                      edgecolor='black',
                                      alpha=0.7)
    ax.add_patch(cache_types_rect)
    ax.text(9.25, 7.7, 'Cache Types', fontsize=12, fontweight='bold', ha='center', color='white')
    
    # Individual cache types
    cache_types = [
        ('Knowledge Cache', 7.2, '• All knowledge items\n• Per character\n• App lifetime'),
        ('Memory Cache', 6.2, '• Status values\n• Events & milestones\n• Active sessions'),
        ('Session Cache', 5.2, '• Topic-based\n• Incremental\n• Session lifetime'),
        ('Voice Cache', 4.2, '• TTS audio\n• Hash-based\n• 24hr TTL')
    ]
    
    for name, y, details in cache_types:
        type_box = FancyBboxPatch((7.3, y-0.35), 4, 0.7,
                                  boxstyle="round,pad=0.02",
                                  facecolor='white',
                                  edgecolor='black',
                                  alpha=0.9)
        ax.add_patch(type_box)
        ax.text(8.5, y+0.15, name, fontsize=9, fontweight='bold', ha='center')
        ax.text(10.3, y-0.05, details, fontsize=6, ha='center', va='center')
    
    # Cache Flow (left side arrows)
    ax.text(0.5, 8.5, 'Request', fontsize=10, fontweight='bold', ha='center')
    
    # Hit/Miss flow
    for i, layer in enumerate(layers):
        if i < len(layers) - 1:
            # Miss arrow (downward)
            arrow = FancyArrowPatch((1.5, layer['y']-0.4), (1.5, layers[i+1]['y']+0.4),
                                   arrowstyle='->,head_width=0.15,head_length=0.15',
                                   color='red', linewidth=1.5)
            ax.add_patch(arrow)
            ax.text(1.2, (layer['y'] + layers[i+1]['y'])/2, 'Miss', 
                   fontsize=7, color='red', ha='right')
        
        # Hit arrow (leftward)
        arrow = FancyArrowPatch((1, layer['y']), (0.3, layer['y']),
                               arrowstyle='->,head_width=0.15,head_length=0.15',
                               color='green', linewidth=1.5)
        ax.add_patch(arrow)
        ax.text(0.2, layer['y']+0.15, 'Hit', fontsize=7, color='green', ha='right')
    
    # Cache Update flow (right side)
    ax.text(6.5, 2.5, 'Cache Update Flow', fontsize=10, fontweight='bold', ha='center')
    
    # Update arrows (upward)
    for i in range(len(layers)-1, 0, -1):
        arrow = FancyArrowPatch((5.5, layers[i]['y']+0.1), (5.5, layers[i-1]['y']-0.1),
                               arrowstyle='->,head_width=0.15,head_length=0.15',
                               color='blue', linewidth=1.5)
        ax.add_patch(arrow)
    
    ax.text(5.8, 5.25, 'Update', fontsize=7, color='blue', rotation=90, va='center')
    
    # Cache Eviction Policy
    eviction_rect = FancyBboxPatch((1, 1), 10, 1.5,
                                   boxstyle="round,pad=0.1",
                                   facecolor='#34495E',
                                   edgecolor='black',
                                   alpha=0.7)
    ax.add_patch(eviction_rect)
    ax.text(6, 2.2, 'Cache Eviction Policies', fontsize=11, fontweight='bold', ha='center', color='white')
    
    policies = [
        'L1: No eviction (app lifetime)',
        'L2: LRU - Least Recently Used',
        'L3: TTL - Time To Live based',
        'L4: Manual cleanup/rotation'
    ]
    
    for i, policy in enumerate(policies):
        ax.text(3 + (i % 2) * 6, 1.7 - (i // 2) * 0.3, policy, 
               fontsize=8, ha='center', color='white')
    
    plt.tight_layout()
    plt.savefig('/Users/bagsanghui/neona_turn_based_demo_with_agent/documents/architecture_cache.png', dpi=300, bbox_inches='tight')
    plt.close()

# Generate all diagrams
if __name__ == "__main__":
    print("Generating architecture diagrams...")
    
    print("1. Creating high-level architecture diagram...")
    create_high_level_architecture()
    
    print("2. Creating RAG system diagram...")
    create_rag_system_diagram()
    
    print("3. Creating memory system diagram...")
    create_memory_system_diagram()
    
    print("4. Creating message flow diagram...")
    create_message_flow_diagram()
    
    print("5. Creating cache architecture diagram...")
    create_cache_architecture_diagram()
    
    print("\nAll diagrams generated successfully!")
    print("Check the /documents/ directory for the PNG files.")