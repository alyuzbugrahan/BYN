import React, { useEffect, useState, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { feedAPI } from '../utils/api';
import { Post, Hashtag } from '../types';
import PostCard from '../components/PostCard';
import LoadingSpinner, { PostSkeleton } from '../components/LoadingSpinner';
import {
  PlusIcon,
  PhotoIcon,
  VideoCameraIcon,
  DocumentTextIcon,
  BriefcaseIcon,
  TrophyIcon,
  SparklesIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

const FeedPage: React.FC = () => {
  const { user } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [trendingHashtags, setTrendingHashtags] = useState<Hashtag[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const [newPostContent, setNewPostContent] = useState('');
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [isCreatingPost, setIsCreatingPost] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const [postType, setPostType] = useState<'text' | 'image' | 'video' | 'document'>('text');
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [feedData, hashtagsData] = await Promise.all([
        feedAPI.getFeed({ page: 1 }),
        feedAPI.getTrendingHashtags().catch(() => [])
      ]);
      
      setPosts(feedData.results);
      setTrendingHashtags(hashtagsData);
      setHasMore(!!feedData.next);
      setPage(2);
    } catch (error) {
      console.error('Error loading feed:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMorePosts = async () => {
    if (!hasMore || loading) return;

    try {
      setLoading(true);
      const feedData = await feedAPI.getFeed({ page });
      setPosts(prev => [...prev, ...feedData.results]);
      setHasMore(!!feedData.next);
      setPage(prev => prev + 1);
    } catch (error) {
      console.error('Error loading more posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (type: 'image' | 'video' | 'document') => {
    const input = fileInputRef.current;
    if (!input) return;

    // Set accepted file types based on selection
    switch (type) {
      case 'image':
        input.accept = 'image/*';
        break;
      case 'video':
        input.accept = 'video/*';
        break;
      case 'document':
        input.accept = '.pdf,.doc,.docx,.txt,.ppt,.pptx,.xls,.xlsx';
        break;
    }

    setPostType(type);
    input.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);

    // Create preview for images and videos
    if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setFilePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setFilePreview(null);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setFilePreview(null);
    setPostType('text');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleCreatePost = async () => {
    if ((!newPostContent.trim() && !selectedFile) || isCreatingPost) return;

    try {
      setIsCreatingPost(true);
      const postData: any = {
        content: newPostContent,
        post_type: postType,
        visibility: 'public'
      };

      if (selectedFile) {
        if (postType === 'image') {
          postData.image = selectedFile;
        } else if (postType === 'video') {
          postData.video = selectedFile;
        } else if (postType === 'document') {
          postData.document = selectedFile;
        }
      }

      const newPost = await feedAPI.createPost(postData);
      
      setPosts(prev => [newPost, ...prev]);
      setNewPostContent('');
      setShowCreatePost(false);
      removeFile();
    } catch (error) {
      console.error('Error creating post:', error);
    } finally {
      setIsCreatingPost(false);
    }
  };

  console.log(trendingHashtags, 'trendingHashtags');
  

  if (loading && posts.length === 0) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            {/* Create Post Skeleton */}
            <div className="bg-white rounded-lg shadow-card border border-gray-200 p-4 mb-6 animate-pulse">
              <div className="flex items-start space-x-3">
                <div className="w-12 h-12 bg-gray-300 rounded-full"></div>
                <div className="flex-1 h-12 bg-gray-200 rounded-lg"></div>
              </div>
            </div>
            
            {/* Post Skeletons */}
            {[...Array(3)].map((_, i) => (
              <PostSkeleton key={i} />
            ))}
          </div>
          
          {/* Sidebar Skeleton */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-card p-6 animate-pulse">
              <div className="h-6 bg-gray-300 rounded w-1/2 mb-4"></div>
              <div className="space-y-2">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-4 bg-gray-200 rounded w-full"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Feed */}
        <div className="lg:col-span-2">
          {/* Create Post */}
          <div className="bg-white rounded-lg shadow-card border border-gray-200 p-4 mb-6 transition-all duration-200 hover:shadow-card-hover">
            <div className="flex items-start space-x-3">
              <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center overflow-hidden">
                {user?.profile_picture ? (
                  <img
                    src={user.profile_picture}
                    alt={`${user.first_name} ${user.last_name}`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-sm font-medium text-gray-700">
                    {user?.first_name?.[0]}{user?.last_name?.[0]}
                  </span>
                )}
              </div>
              
              <div className="flex-1">
                {showCreatePost ? (
                  <div className="space-y-3 animate-slide-up">
                    <textarea
                      value={newPostContent}
                      onChange={(e) => setNewPostContent(e.target.value)}
                      placeholder="What's on your mind?"
                      className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-byn-500 focus:border-transparent transition-all duration-200"
                      rows={4}
                      autoFocus
                    />
                    
                    {/* File Preview */}
                    {selectedFile && (
                      <div className="relative border border-gray-200 rounded-lg p-3 bg-gray-50">
                        <button
                          onClick={removeFile}
                          className="absolute top-2 right-2 p-1 bg-white rounded-full shadow-sm hover:bg-gray-100 transition-colors duration-200"
                        >
                          <XMarkIcon className="w-4 h-4 text-gray-500" />
                        </button>
                        
                        {filePreview && postType === 'image' && (
                          <img
                            src={filePreview}
                            alt="Preview"
                            className="max-h-64 w-full object-cover rounded-lg"
                          />
                        )}
                        
                        {filePreview && postType === 'video' && (
                          <video
                            src={filePreview}
                            controls
                            className="max-h-64 w-full rounded-lg"
                          />
                        )}
                        
                        {postType === 'document' && (
                          <div className="flex items-center space-x-3 p-3">
                            <DocumentTextIcon className="w-8 h-8 text-byn-500" />
                            <div>
                              <p className="font-medium text-gray-900">{selectedFile.name}</p>
                              <p className="text-sm text-gray-500">
                                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 text-gray-500">
                        <button 
                          onClick={() => handleFileSelect('image')}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 hover:text-byn-600"
                          title="Add photo"
                        >
                          <PhotoIcon className="w-5 h-5" />
                        </button>
                        <button 
                          onClick={() => handleFileSelect('video')}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 hover:text-byn-600"
                          title="Add video"
                        >
                          <VideoCameraIcon className="w-5 h-5" />
                        </button>
                        <button 
                          onClick={() => handleFileSelect('document')}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 hover:text-byn-600"
                          title="Add document"
                        >
                          <DocumentTextIcon className="w-5 h-5" />
                        </button>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => {
                            setShowCreatePost(false);
                            setNewPostContent('');
                            removeFile();
                          }}
                          className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors duration-200"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={handleCreatePost}
                          disabled={(!newPostContent.trim() && !selectedFile) || isCreatingPost}
                          className="px-6 py-2 bg-byn-500 text-white rounded-lg hover:bg-byn-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
                        >
                          {isCreatingPost ? (
                            <div className="flex items-center space-x-2">
                              <LoadingSpinner size="small" />
                              <span>Posting...</span>
                            </div>
                          ) : (
                            'Post'
                          )}
                        </button>
                      </div>
                    </div>
                    
                    {/* Hidden file input */}
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </div>
                ) : (
                  <button
                    onClick={() => setShowCreatePost(true)}
                    className="w-full text-left p-3 border border-gray-300 rounded-lg text-gray-500 hover:border-byn-300 hover:text-byn-600 transition-all duration-200 hover:shadow-md"
                  >
                    Start a post...
                  </button>
                )}
              </div>
            </div>
            
            {!showCreatePost && (
              <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
                <button 
                  onClick={() => {
                    setShowCreatePost(true);
                    setTimeout(() => handleFileSelect('image'), 100);
                  }}
                  className="flex items-center space-x-2 px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 hover:text-byn-600"
                >
                  <PhotoIcon className="w-5 h-5" />
                  <span>Photo</span>
                </button>
                <button 
                  onClick={() => {
                    setShowCreatePost(true);
                    setTimeout(() => handleFileSelect('video'), 100);
                  }}
                  className="flex items-center space-x-2 px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 hover:text-byn-600"
                >
                  <VideoCameraIcon className="w-5 h-5" />
                  <span>Video</span>
                </button>
                <button 
                  onClick={() => setShowCreatePost(true)}
                  className="flex items-center space-x-2 px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 hover:text-byn-600"
                >
                  <BriefcaseIcon className="w-5 h-5" />
                  <span>Job</span>
                </button>
                <button 
                  onClick={() => {
                    setShowCreatePost(true);
                    setTimeout(() => handleFileSelect('document'), 100);
                  }}
                  className="flex items-center space-x-2 px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 hover:text-byn-600"
                >
                  <DocumentTextIcon className="w-5 h-5" />
                  <span>Article</span>
                </button>
              </div>
            )}
          </div>

          {/* Posts Feed */}
          <div className="space-y-6">
            {posts.map((post, index) => (
              <div key={post.id} style={{ animationDelay: `${index * 100}ms` }} className="animate-fade-in">
                <PostCard
                  post={post}
                  onUpdate={(updatedPost) => {
                    setPosts(prev => prev.map(p => p.id === updatedPost.id ? updatedPost : p));
                  }}
                  onDelete={(postId) => {
                    setPosts(prev => prev.filter(p => p.id !== postId));
                  }}
                />
              </div>
            ))}
          </div>

          {/* Load More */}
          {hasMore && (
            <div className="text-center mt-8">
              <button
                onClick={loadMorePosts}
                disabled={loading}
                className="px-6 py-3 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-all duration-200 hover:shadow-md"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <LoadingSpinner size="small" />
                    <span>Loading...</span>
                  </div>
                ) : (
                  'Load more posts'
                )}
              </button>
            </div>
          )}

          {posts.length === 0 && !loading && (
            <div className="bg-white rounded-lg shadow-card border border-gray-200 p-8 text-center animate-fade-in">
              <SparklesIcon className="w-16 h-16 text-byn-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Welcome to BYN!</h3>
              <p className="text-gray-600 mb-4">
                Start following people or companies to see posts in your feed.
              </p>
              <button
                onClick={() => setShowCreatePost(true)}
                className="inline-flex items-center px-4 py-2 bg-byn-500 text-white rounded-lg hover:bg-byn-600 transition-all duration-200 transform hover:scale-105"
              >
                <PlusIcon className="w-5 h-5 mr-2" />
                Create your first post
              </button>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Trending Hashtags */}
          {trendingHashtags.length > 0 && (
            <div className="bg-white rounded-lg shadow-card border border-gray-200 p-6 animate-fade-in">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <TrophyIcon className="w-5 h-5 mr-2 text-byn-500" />
                Trending
              </h3>
              <div className="space-y-3">
                {trendingHashtags.slice(0, 5).map((hashtag, index) => (
                  <div key={hashtag.id} className="flex items-center justify-between group">
                    <span className="text-byn-600 font-medium group-hover:text-byn-700 transition-colors duration-200">
                      #{hashtag.name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {hashtag.posts_count} posts
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Tips */}
          <div className="bg-gradient-to-br from-byn-50 to-blue-50 rounded-lg p-6 border border-byn-200 animate-fade-in">
            <h3 className="text-lg font-semibold text-byn-900 mb-4 flex items-center">
              <SparklesIcon className="w-5 h-5 mr-2 text-byn-500" />
              Tips for Better Engagement
            </h3>
            <div className="space-y-3 text-sm text-byn-800">
              <p className="flex items-start">
                <span className="text-byn-500 mr-2">•</span>
                Use relevant hashtags to reach more people
              </p>
              <p className="flex items-start">
                <span className="text-byn-500 mr-2">•</span>
                Share industry insights and experiences
              </p>
              <p className="flex items-start">
                <span className="text-byn-500 mr-2">•</span>
                Engage with others' posts through comments
              </p>
              <p className="flex items-start">
                <span className="text-byn-500 mr-2">•</span>
                Post consistently to build your network
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeedPage; 