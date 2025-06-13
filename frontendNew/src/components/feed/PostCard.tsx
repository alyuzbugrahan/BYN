'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { Post } from '../../types';
import { feedAPI } from '../../utils/api';
import { useAuth } from '../../contexts/AuthContext';
import CommentsSection from './CommentsSection';
import {
  HeartIcon,
  ChatBubbleOvalLeftIcon,
  ShareIcon,
  BookmarkIcon,
  EllipsisHorizontalIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import {
  HeartIcon as HeartSolid,
  BookmarkIcon as BookmarkSolid,
} from '@heroicons/react/24/solid';
import { toast } from 'react-toastify';

interface PostCardProps {
  post: Post;
  onUpdate?: (updatedPost: Post) => void;
  onDelete?: (postId: number) => void;
}

const PostCard: React.FC<PostCardProps> = ({ post, onUpdate, onDelete }) => {
  const { user } = useAuth();
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [isLiked, setIsLiked] = useState(post.user_has_liked || false);
  const [isSaved, setIsSaved] = useState(post.user_has_saved || false);
  const [likesCount, setLikesCount] = useState(post.likes_count);
  const [commentsCount, setCommentsCount] = useState(post.comments_count);
  const [showComments, setShowComments] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(post.content);
  const [editVisibility, setEditVisibility] = useState(post.visibility);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLike = async () => {
    if (isLoading) return;
    
    try {
      setIsLoading(true);
      const response = await feedAPI.likePost(post.id);
      
      if (response.status === 'liked') {
        setIsLiked(true);
        setLikesCount(prev => prev + 1);
      } else if (response.status === 'unliked') {
        setIsLiked(false);
        setLikesCount(prev => prev - 1);
      }
    } catch (error) {
      console.error('Error toggling like:', error);
      toast.error('Failed to update like');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (isLoading) return;
    
    try {
      setIsLoading(true);
      if (isSaved) {
        await feedAPI.unsavePost(post.id);
        setIsSaved(false);
        toast.success('Post unsaved');
      } else {
        await feedAPI.savePost(post.id);
        setIsSaved(true);
        toast.success('Post saved');
      }
    } catch (error) {
      console.error('Error toggling save:', error);
      toast.error('Failed to update save status');
    } finally {
      setIsLoading(false);
    }
  };

  const handleShare = async () => {
    try {
      await feedAPI.sharePost(post.id);
      toast.success('Post shared successfully');
    } catch (error) {
      console.error('Error sharing post:', error);
      toast.error('Failed to share post');
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
    setShowDropdown(false);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditContent(post.content);
    setEditVisibility(post.visibility);
  };

  const handleSaveEdit = async () => {
    if (!editContent.trim()) {
      toast.error('Post content cannot be empty');
      return;
    }

    try {
      setIsLoading(true);
      const updatedPost = await feedAPI.updatePost(post.id, {
        content: editContent,
        visibility: editVisibility,
      });
      
      setIsEditing(false);
      toast.success('Post updated successfully');
      
      if (onUpdate) {
        onUpdate(updatedPost);
      }
    } catch (error) {
      console.error('Error updating post:', error);
      toast.error('Failed to update post');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
      return;
    }

    try {
      setIsLoading(true);
      await feedAPI.deletePost(post.id);
      toast.success('Post deleted successfully');
      
      if (onDelete) {
        onDelete(post.id);
      }
    } catch (error) {
      console.error('Error deleting post:', error);
      toast.error('Failed to delete post');
    } finally {
      setIsLoading(false);
      setShowDropdown(false);
    }
  };

  const renderPostContent = () => {
    if (isEditing) {
      return (
        <div className="space-y-3">
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-primary-500 focus:border-primary-500"
            rows={4}
            placeholder="What's on your mind?"
          />
          <div className="flex items-center justify-between">
            <select
              value={editVisibility}
              onChange={(e) => setEditVisibility(e.target.value as 'public' | 'connections' | 'private')}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="public">Public</option>
              <option value="connections">Connections only</option>
              <option value="private">Private</option>
            </select>
            <div className="flex space-x-2">
              <button
                onClick={handleCancelEdit}
                disabled={isLoading}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                disabled={isLoading || !editContent.trim()}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
              >
                {isLoading ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      );
    }

    const content = post.content;
    const processedContent = content
      .replace(/#(\w+)/g, '<span class="text-primary-600 font-medium">#$1</span>')
      .replace(/@(\w+)/g, '<span class="text-primary-600 font-medium">@$1</span>');
    
    return <div dangerouslySetInnerHTML={{ __html: processedContent }} />;
  };

  const canEdit = post.can_edit || (user && post.author.id === user.id);
  const canDelete = post.can_delete || (user && post.author.id === user.id);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-4 transition-all duration-200 hover:shadow-md">
      {/* Post Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <Link href={`/profile/${post.author.id}`} className="group">
              <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center overflow-hidden transition-transform duration-200 group-hover:scale-105">
                {post.author.profile_picture_url ? (
                  <img
                    src={post.author.profile_picture_url}
                    alt={`${post.author.first_name} ${post.author.last_name}`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-sm font-medium text-gray-700">
                    {post.author.first_name?.[0]}{post.author.last_name?.[0]}
                  </span>
                )}
              </div>
            </Link>
            
            <div>
              <Link 
                href={`/profile/${post.author.id}`}
                className="font-semibold text-gray-900 hover:text-primary-600 transition-colors duration-200"
              >
                {post.author.first_name} {post.author.last_name}
              </Link>
              {post.author.headline && (
                <p className="text-sm text-gray-600">{post.author.headline}</p>
              )}
              <p className="text-xs text-gray-500">
                {formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}
                {post.visibility !== 'public' && (
                  <span className="ml-2 text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                    {post.visibility === 'connections' ? 'Connections only' : 'Private'}
                  </span>
                )}
              </p>
            </div>
          </div>
          
          {(canEdit || canDelete) && (
            <div className="relative" ref={dropdownRef}>
              <button 
                onClick={() => setShowDropdown(!showDropdown)}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-all duration-200"
              >
                <EllipsisHorizontalIcon className="w-5 h-5" />
              </button>
              
              {showDropdown && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10">
                  <div className="py-1">
                    {canEdit && (
                      <button
                        onClick={handleEdit}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors duration-150"
                      >
                        <PencilIcon className="w-4 h-4 mr-3" />
                        Edit post
                      </button>
                    )}
                    {canDelete && (
                      <button
                        onClick={handleDelete}
                        disabled={isLoading}
                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50 transition-colors duration-150"
                      >
                        <TrashIcon className="w-4 h-4 mr-3" />
                        Delete post
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Post Content */}
      <div className="p-4">
        <div className="text-gray-900 mb-3">
          {renderPostContent()}
        </div>

        {/* Post Image */}
        {post.image && !isEditing && (
          <div className="mb-3 group">
            <img
              src={post.image}
              alt="Post content"
              className="w-full max-h-96 object-cover rounded-lg transition-transform duration-300 group-hover:scale-[1.02]"
            />
          </div>
        )}

        {/* Shared Job */}
        {post.shared_job && !isEditing && (
          <div className="border border-gray-200 rounded-lg p-4 mb-3 bg-gray-50 transition-all duration-200 hover:bg-gray-100 hover:border-primary-300">
            <Link 
              href={`/jobs/${post.shared_job.id}`}
              className="block hover:bg-gray-100 rounded-lg p-2 -m-2 transition-colors duration-200"
            >
              <h4 className="font-semibold text-gray-900">{post.shared_job.title}</h4>
              <p className="text-sm text-gray-600">{post.shared_job.company.name}</p>
              <p className="text-xs text-gray-500">{post.shared_job.location}</p>
            </Link>
          </div>
        )}

        {/* Article Link */}
        {post.article_url && !isEditing && (
          <div className="border border-gray-200 rounded-lg p-4 mb-3 transition-all duration-200 hover:border-primary-300 hover:shadow-md">
            <a 
              href={post.article_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block hover:bg-gray-50 rounded-lg p-2 -m-2 transition-colors duration-200"
            >
              {post.article_image && (
                <img
                  src={post.article_image}
                  alt={post.article_title}
                  className="w-full h-32 object-cover rounded mb-2 transition-transform duration-300 hover:scale-[1.02]"
                />
              )}
              <h4 className="font-semibold text-gray-900">{post.article_title}</h4>
              {post.article_description && (
                <p className="text-sm text-gray-600 mt-1">{post.article_description}</p>
              )}
            </a>
          </div>
        )}

        {/* Hashtags */}
        {post.hashtags && post.hashtags.length > 0 && !isEditing && (
          <div className="flex flex-wrap gap-2 mb-3">
            {post.hashtags.map((hashtag) => (
              <Link
                key={hashtag.id}
                href={`/hashtag/${hashtag.name}`}
                className="text-primary-600 text-sm hover:underline hover:text-primary-700 transition-colors duration-200 px-2 py-1 rounded-full hover:bg-primary-50"
              >
                #{hashtag.name}
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Engagement Stats */}
      {(likesCount > 0 || commentsCount > 0 || post.shares_count > 0) && !isEditing && (
        <div className="px-4 py-2 border-t border-gray-100 text-sm text-gray-600">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {likesCount > 0 && (
                <span className="hover:text-primary-600 transition-colors duration-200 cursor-default">
                  {likesCount} {likesCount === 1 ? 'like' : 'likes'}
                </span>
              )}
              {commentsCount > 0 && (
                <button
                  onClick={() => setShowComments(!showComments)}
                  className="hover:text-primary-600 transition-colors duration-200"
                >
                  {commentsCount} {commentsCount === 1 ? 'comment' : 'comments'}
                </button>
              )}
            </div>
            {post.shares_count > 0 && (
              <span className="hover:text-primary-600 transition-colors duration-200 cursor-default">
                {post.shares_count} {post.shares_count === 1 ? 'share' : 'shares'}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {!isEditing && (
        <div className="px-4 py-3 border-t border-gray-100">
          <div className="flex items-center justify-between">
            <button
              onClick={handleLike}
              disabled={isLoading}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isLiked
                  ? 'text-primary-600 bg-primary-50 hover:bg-primary-100'
                  : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
              }`}
            >
              {isLiked ? (
                <HeartSolid className="w-5 h-5" />
              ) : (
                <HeartIcon className="w-5 h-5" />
              )}
              <span>Like</span>
            </button>

            <button
              onClick={() => setShowComments(!showComments)}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-primary-600 hover:bg-gray-100 transition-all duration-200"
            >
              <ChatBubbleOvalLeftIcon className="w-5 h-5" />
              <span>Comment</span>
            </button>

            <button
              onClick={handleShare}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-primary-600 hover:bg-gray-100 transition-all duration-200"
            >
              <ShareIcon className="w-5 h-5" />
              <span>Share</span>
            </button>

            <button
              onClick={handleSave}
              disabled={isLoading}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isSaved
                  ? 'text-primary-600 bg-primary-50 hover:bg-primary-100'
                  : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
              }`}
            >
              {isSaved ? (
                <BookmarkSolid className="w-5 h-5" />
              ) : (
                <BookmarkIcon className="w-5 h-5" />
              )}
              <span>Save</span>
            </button>
          </div>
        </div>
      )}

      {/* Comments Section */}
      {showComments && !isEditing && (
        <div className="border-t border-gray-100 p-4 bg-gray-50">
          <CommentsSection 
            postId={post.id} 
            commentsCount={commentsCount}
            onCommentsCountChange={setCommentsCount}
          />
        </div>
      )}
    </div>
  );
};

export default PostCard;
