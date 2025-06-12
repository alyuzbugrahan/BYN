import React, { useState, useEffect } from 'react';
import { feedAPI } from '../utils/api';
import { Comment } from '../types';
import { useAuth } from '../contexts/AuthContext';
import {
  HeartIcon,
  ChatBubbleOvalLeftIcon,
  PaperAirplaneIcon,
  EllipsisHorizontalIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import {
  HeartIcon as HeartSolid,
} from '@heroicons/react/24/solid';
import LoadingSpinner, { CommentSkeleton } from './LoadingSpinner';
import { formatDistanceToNow } from 'date-fns';

interface CommentsSectionProps {
  postId: number;
  commentsCount: number;
  onCommentsCountChange: (newCount: number) => void;
}

const CommentsSection: React.FC<CommentsSectionProps> = ({ 
  postId, 
  commentsCount, 
  onCommentsCountChange 
}) => {
  const { user } = useAuth();
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [editingCommentId, setEditingCommentId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState('');

  useEffect(() => {
    loadComments();
  }, [postId]);

  const loadComments = async () => {
    try {
      setLoading(true);
      const response = await feedAPI.getComments(postId);
      setComments(response.results);
    } catch (error) {
      console.error('Error loading comments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || submitting) return;

    try {
      setSubmitting(true);
      const comment = await feedAPI.createComment(postId, newComment.trim());
      
      setComments(prev => [comment, ...prev]);
      setNewComment('');
      onCommentsCountChange(commentsCount + 1);
    } catch (error) {
      console.error('Error creating comment:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleLikeComment = async (commentId: number) => {
    try {
      await feedAPI.likeComment(commentId);
      setComments(prev => prev.map(comment => 
        comment.id === commentId 
          ? { 
              ...comment, 
              user_has_liked: !comment.user_has_liked,
              likes_count: comment.user_has_liked 
                ? comment.likes_count - 1 
                : comment.likes_count + 1
            }
          : comment
      ));
    } catch (error) {
      console.error('Error liking comment:', error);
    }
  };

  const handleEditComment = (comment: Comment) => {
    setEditingCommentId(comment.id);
    setEditContent(comment.content);
  };

  const handleSaveEdit = async (commentId: number) => {
    if (!editContent.trim()) return;

    try {
      const updatedComment = await feedAPI.updateComment(commentId, editContent.trim());
      
      setComments(prev => prev.map(comment => 
        comment.id === commentId ? updatedComment : comment
      ));
      setEditingCommentId(null);
      setEditContent('');
    } catch (error) {
      console.error('Error updating comment:', error);
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) return;

    try {
      await feedAPI.deleteComment(commentId);
      setComments(prev => prev.filter(comment => comment.id !== commentId));
      onCommentsCountChange(commentsCount - 1);
    } catch (error) {
      console.error('Error deleting comment:', error);
    }
  };

  const renderComment = (comment: Comment, index: number) => {
    const isEditing = editingCommentId === comment.id;
    const canEdit = comment.can_edit || (user && comment.author.id === user.id);
    const canDelete = comment.can_delete || (user && comment.author.id === user.id);

    return (
      <div 
        key={comment.id} 
        className="flex space-x-3 animate-fade-in-up group"
        style={{ animationDelay: `${index * 100}ms` }}
      >
        <div className="flex-shrink-0">
          {comment.author.profile_picture_url ? (
            <img
              src={comment.author.profile_picture_url}
              alt={comment.author.first_name}
              className="w-8 h-8 rounded-full object-cover transition-transform duration-200 group-hover:scale-105"
            />
          ) : (
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center transition-transform duration-200 group-hover:scale-105">
              <span className="text-xs font-medium text-gray-600">
                {comment.author.first_name?.[0]}{comment.author.last_name?.[0]}
              </span>
            </div>
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="bg-gray-100 rounded-lg px-3 py-2 transition-all duration-200 group-hover:bg-gray-50">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 hover:text-byn-600 transition-colors duration-200">
                  {comment.author.first_name} {comment.author.last_name}
                </p>
                
                {isEditing ? (
                  <div className="mt-1 space-y-2">
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      className="w-full p-2 text-sm border border-gray-300 rounded focus:ring-byn-500 focus:border-byn-500 resize-none"
                      rows={2}
                      autoFocus
                    />
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleSaveEdit(comment.id)}
                        disabled={!editContent.trim()}
                        className="px-3 py-1 text-xs bg-byn-500 text-white rounded hover:bg-byn-600 disabled:opacity-50 transition-colors duration-200"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => {
                          setEditingCommentId(null);
                          setEditContent('');
                        }}
                        className="px-3 py-1 text-xs text-gray-600 hover:text-gray-800 transition-colors duration-200"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <p className="mt-1 text-sm text-gray-700">{comment.content}</p>
                )}
              </div>
              
              {(canEdit || canDelete) && !isEditing && (
                <div className="relative group/dropdown">
                  <button className="p-1 text-gray-400 hover:text-gray-600 rounded opacity-0 group-hover:opacity-100 transition-all duration-200">
                    <EllipsisHorizontalIcon className="w-4 h-4" />
                  </button>
                  
                  <div className="absolute right-0 top-6 w-32 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10 opacity-0 group-hover/dropdown:opacity-100 transition-opacity duration-200 pointer-events-none group-hover/dropdown:pointer-events-auto">
                    <div className="py-1">
                      {canEdit && (
                        <button
                          onClick={() => handleEditComment(comment)}
                          className="flex items-center w-full px-3 py-2 text-xs text-gray-700 hover:bg-gray-100 transition-colors duration-150"
                        >
                          <PencilIcon className="w-3 h-3 mr-2" />
                          Edit
                        </button>
                      )}
                      {canDelete && (
                        <button
                          onClick={() => handleDeleteComment(comment.id)}
                          className="flex items-center w-full px-3 py-2 text-xs text-red-600 hover:bg-red-50 transition-colors duration-150"
                        >
                          <TrashIcon className="w-3 h-3 mr-2" />
                          Delete
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
            <span className="hover:text-byn-600 transition-colors duration-200">
              {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
            </span>
            
            <button
              onClick={() => handleLikeComment(comment.id)}
              className={`flex items-center space-x-1 hover:text-byn-600 transition-all duration-200 ${
                comment.user_has_liked ? 'text-byn-600' : 'text-gray-500'
              }`}
            >
              {comment.user_has_liked ? (
                <HeartSolid className="w-3 h-3 animate-pulse" />
              ) : (
                <HeartIcon className="w-3 h-3" />
              )}
              <span>{comment.likes_count > 0 ? comment.likes_count : 'Like'}</span>
            </button>
            
            <button className="hover:text-byn-600 transition-colors duration-200">
              Reply
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Add Comment Form */}
      <form onSubmit={handleSubmitComment} className="flex space-x-3">
        <div className="flex-shrink-0">
          {user?.profile_picture ? (
            <img
              src={user.profile_picture}
              alt={user.first_name}
              className="w-8 h-8 rounded-full object-cover"
            />
          ) : (
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <span className="text-xs font-medium text-gray-600">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </span>
            </div>
          )}
        </div>
        <div className="flex-1">
          <div className="flex items-end space-x-2">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Write a comment..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:ring-byn-500 focus:border-byn-500 transition-all duration-200"
              rows={1}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = target.scrollHeight + 'px';
              }}
            />
            <button
              type="submit"
              disabled={!newComment.trim() || submitting}
              className="px-3 py-2 bg-byn-500 text-white rounded-lg hover:bg-byn-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
            >
              {submitting ? (
                <LoadingSpinner size="small" />
              ) : (
                <PaperAirplaneIcon className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Comments List */}
      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <CommentSkeleton key={i} />
          ))}
        </div>
      ) : comments.length > 0 ? (
        <div className="space-y-4">
          {comments.map((comment, index) => renderComment(comment, index))}
        </div>
      ) : (
        <div className="text-center py-4 text-gray-500 animate-fade-in">
          <ChatBubbleOvalLeftIcon className="w-8 h-8 mx-auto mb-2 text-gray-300" />
          <p className="text-sm">No comments yet. Be the first to comment!</p>
        </div>
      )}
    </div>
  );
};

export default CommentsSection; 