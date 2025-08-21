import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Edit, Trash2, User } from 'lucide-react';
import { Character } from '@/types/character';
// Knowledge management integration - minimal for TDD GREEN phase
// TODO: Add knowledge display and management UI

interface CharacterCardProps {
  character: Character;
  onClick: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onPersona?: () => void;
}

export function CharacterCard({ 
  character, 
  onClick, 
  onEdit, 
  onDelete,
  onPersona 
}: CharacterCardProps) {
  return (
    <Card 
      className="cursor-pointer hover:shadow-lg transition-shadow relative group"
      onClick={onClick}
    >
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1 z-10">
        {onPersona && (
          <Button
            size="sm"
            variant="ghost"
            className="h-8 w-8 p-0"
            onClick={(e) => {
              e.stopPropagation();
              onPersona();
            }}
            title="페르소나 관리"
          >
            <User className="w-4 h-4" />
          </Button>
        )}
        {onEdit && (
          <Button
            size="sm"
            variant="ghost"
            className="h-8 w-8 p-0"
            onClick={(e) => {
              e.stopPropagation();
              onEdit();
            }}
          >
            <Edit className="w-4 h-4" />
          </Button>
        )}
        {onDelete && (
          <Button
            size="sm"
            variant="ghost"
            className="h-8 w-8 p-0"
            onClick={(e) => {
              e.stopPropagation();
              if (confirm('정말 삭제하시겠습니까?')) {
                onDelete();
              }
            }}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        )}
      </div>
      
      <CardContent className="p-4">
        <div className="aspect-square mb-3 overflow-hidden rounded-lg bg-muted">
          {character.image ? (
            <img 
              src={character.image} 
              alt={character.name}
              className="w-full h-full object-cover object-top"
              onError={(e) => {
                // Fallback to letter avatar if image fails
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                const fallback = target.nextElementSibling as HTMLDivElement;
                if (fallback) fallback.style.display = 'flex';
              }}
            />
          ) : null}
          <div 
            className="w-full h-full flex items-center justify-center text-4xl font-bold text-muted-foreground"
            style={{ display: character.image ? 'none' : 'flex' }}
          >
            {character.name[0]?.toUpperCase() || '?'}
          </div>
        </div>
        <h3 className="font-bold text-lg mb-1">{character.name}</h3>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {character.description}
        </p>
      </CardContent>
    </Card>
  );
}