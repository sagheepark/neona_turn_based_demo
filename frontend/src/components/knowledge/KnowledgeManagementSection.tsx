/**
 * Knowledge Management Section Component
 * Redesigned with shadcn components for consistency
 */

import React, { useState, useEffect } from 'react';
import { ApiClient } from '@/lib/api-client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Collapsible } from '@/components/ui/collapsible';
import { Plus, X, Brain, Tag } from 'lucide-react';

interface KnowledgeItem {
  id?: string;
  title: string;
  content: string;
  keywords: string[];
  category?: string;
  priority?: number;
  created_at?: string;
}

interface KnowledgeManagementSectionProps {
  characterId?: string;
  knowledgeItems?: KnowledgeItem[];
  onKnowledgeChange?: (items: KnowledgeItem[]) => void;
}

export function KnowledgeManagementSection({ 
  characterId, 
  knowledgeItems = [], 
  onKnowledgeChange 
}: KnowledgeManagementSectionProps) {
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingItem, setEditingItem] = useState<string | null>(null);

  // Load existing knowledge items when component mounts or characterId changes
  useEffect(() => {
    if (characterId) {
      loadKnowledgeItems();
    }
  }, [characterId]);

  const loadKnowledgeItems = async () => {
    if (!characterId) return;
    
    try {
      setLoading(true);
      setError(null);
      console.log('Loading knowledge items for character:', characterId);
      const loadedItems = await ApiClient.getCharacterKnowledge(characterId);
      console.log('Loaded knowledge items:', loadedItems);
      setItems(loadedItems);
      onKnowledgeChange?.(loadedItems);
    } catch (error) {
      console.error('Failed to load knowledge items:', error);
      setError('Failed to load knowledge items');
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = () => {
    const newItem: KnowledgeItem = {
      id: `temp_${Date.now()}`,
      title: 'New Knowledge Item',
      content: 'Enter description here...',
      keywords: ['example'],
      category: 'general',
      priority: 1
    };
    const updatedItems = [...items, newItem];
    setItems(updatedItems);
    setEditingItem(newItem.id!);
    onKnowledgeChange?.(updatedItems);
  };

  const handleUpdateItem = (id: string, field: keyof KnowledgeItem, value: any) => {
    const updatedItems = items.map(item => 
      item.id === id ? { ...item, [field]: value } : item
    );
    setItems(updatedItems);
    onKnowledgeChange?.(updatedItems);
  };

  const handleSaveItem = async (id: string) => {
    if (characterId) {
      try {
        const item = items.find(i => i.id === id);
        if (item) {
          await ApiClient.saveCharacterKnowledge(characterId, [item]);
        }
      } catch (error) {
        console.error('Failed to save knowledge item:', error);
      }
    }
    setEditingItem(null);
  };

  const handleRemoveItem = (index: number) => {
    const updatedItems = items.filter((_, i) => i !== index);
    setItems(updatedItems);
    onKnowledgeChange?.(updatedItems);
  };

  console.log('KnowledgeManagementSection rendering with:', { characterId, items: items.length, loading, error });

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5" />
          <CardTitle>Knowledge Base Management</CardTitle>
          {loading && <span className="text-sm text-muted-foreground">(Loading...)</span>}
        </div>
        <CardDescription>
          Add knowledge items that the character can reference during conversations
          {characterId && <span className="text-blue-600 ml-1 font-mono">({characterId})</span>}
        </CardDescription>
        {error && (
          <div className="mt-2 p-3 bg-destructive/15 border border-destructive/20 rounded-md text-destructive text-sm">
            Error: {error}
          </div>
        )}
      </CardHeader>
      <CardContent>

        {loading ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Loading knowledge items...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">No knowledge items found</p>
            <Button type="button" onClick={handleAddItem} variant="outline">
              <Plus className="w-4 h-4 mr-2" />
              Add Knowledge Item
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <Collapsible title="Knowledge Items" defaultOpen>
              <ScrollArea className="h-80 pr-4">
                <div className="space-y-3">
                  {items.map((item, index) => (
                    <Card key={item.id || index} className="p-4">
                      {editingItem === item.id ? (
                        <div className="space-y-3">
                          <div>
                            <Label htmlFor={`title-${item.id}`}>Title</Label>
                            <Input
                              id={`title-${item.id}`}
                              value={item.title}
                              onChange={(e) => handleUpdateItem(item.id!, 'title', e.target.value)}
                            />
                          </div>
                          <div>
                            <Label htmlFor={`content-${item.id}`}>Content</Label>
                            <Textarea
                              id={`content-${item.id}`}
                              value={item.content}
                              onChange={(e) => handleUpdateItem(item.id!, 'content', e.target.value)}
                              rows={3}
                            />
                          </div>
                          <div>
                            <Label htmlFor={`keywords-${item.id}`}>Keywords (comma-separated)</Label>
                            <Input
                              id={`keywords-${item.id}`}
                              value={item.keywords?.join(', ') || ''}
                              onChange={(e) => handleUpdateItem(item.id!, 'keywords', e.target.value.split(',').map(k => k.trim()))}
                            />
                          </div>
                          <div className="flex gap-2">
                            <Button type="button" size="sm" onClick={() => handleSaveItem(item.id!)}>
                              Save
                            </Button>
                            <Button type="button" size="sm" variant="outline" onClick={() => setEditingItem(null)}>
                              Cancel
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-medium">{item.title}</h4>
                            <div className="flex gap-1">
                              <Button 
                                type="button"
                                size="icon" 
                                variant="ghost" 
                                onClick={() => setEditingItem(item.id!)}
                                className="h-6 w-6"
                              >
                                ✏️
                              </Button>
                              <Button 
                                type="button"
                                size="icon" 
                                variant="ghost" 
                                onClick={() => handleRemoveItem(index)}
                                className="h-6 w-6 text-destructive hover:text-destructive"
                              >
                                <X className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">{item.content}</p>
                          <div className="flex flex-wrap gap-1">
                            {item.keywords?.map((keyword, i) => (
                              <span key={i} className="inline-flex items-center gap-1 px-2 py-1 bg-secondary text-secondary-foreground text-xs rounded-md">
                                <Tag className="w-3 h-3" />
                                {keyword}
                              </span>
                            ))}
                          </div>
                          {item.category && (
                            <div className="mt-2">
                              <span className="text-xs text-muted-foreground">Category: {item.category}</span>
                            </div>
                          )}
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              </ScrollArea>
              <div className="pt-3">
                <Button type="button" onClick={handleAddItem} variant="outline" className="w-full">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Knowledge Item
                </Button>
              </div>
            </Collapsible>
          </div>
        )}
      </CardContent>
    </Card>
  );
}