import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usersAPI, feedAPI, authAPI, connectionsAPI } from '../utils/api';
import { User, Experience, Education, UserSkill, Post } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  UserIcon,
  MapPinIcon,
  BriefcaseIcon,
  AcademicCapIcon,
  PencilIcon,
  PlusIcon,
  EnvelopeIcon,
  LinkIcon,
  CalendarIcon,
  BuildingOfficeIcon,
  ExclamationTriangleIcon,
  CameraIcon,
  XMarkIcon,
  TagIcon
} from '@heroicons/react/24/outline';
import {
  CheckBadgeIcon
} from '@heroicons/react/24/solid';

const ProfilePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user: currentUser } = useAuth();
  
  const [user, setUser] = useState<User | null>(null);
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [education, setEducation] = useState<Education[]>([]);
  const [skills, setSkills] = useState<UserSkill[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingProfile, setEditingProfile] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'none' | 'pending' | 'connected'>('none');
  const [addingSkill, setAddingSkill] = useState(false);
  const [addingExperience, setAddingExperience] = useState(false);
  const [addingEducation, setAddingEducation] = useState(false);
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    headline: '',
    current_position: '',
    location: '',
    industry: '',
    about: '',
    phone_number: '',
    website: '',
    experience_level: 'entry' as 'intern' | 'entry' | 'associate' | 'mid' | 'senior' | 'executive'
  });
  
  // Separate state for bio notes
  const [bioNotes, setBioNotes] = useState<string[]>([]);
  const [newBioNote, setNewBioNote] = useState('');
  const [skillForm, setSkillForm] = useState({
    name: '',
    proficiency: 'intermediate' as 'beginner' | 'intermediate' | 'advanced' | 'expert'
  });
  const [experienceForm, setExperienceForm] = useState({
    title: '',
    company: '',
    location: '',
    start_date: '',
    end_date: '',
    is_current: false,
    description: ''
  });
  const [educationForm, setEducationForm] = useState({
    school: '',
    degree: '',
    field_of_study: '',
    start_year: '',
    end_year: '',
    description: ''
  });

  
  // Determine if viewing own profile
  const isOwnProfile = !id || (currentUser && id === currentUser.id.toString());
  const profileUserId = isOwnProfile ? currentUser?.id : parseInt(id || '0');

  useEffect(() => {
    fetchProfileData();
    checkConnectionStatus();
  }, [id, currentUser]);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      
      let userData: User;
      if (isOwnProfile) {
        userData = currentUser!;
      } else {
        userData = await usersAPI.getUserProfile(profileUserId!);
      }
      
      setUser(userData);
      
      // Initialize edit form with user data
      setEditForm({
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        headline: userData.headline || '',
        current_position: userData.current_position || '',
        location: userData.location || '',
        industry: userData.industry || '',
        about: userData.about || '',
        phone_number: userData.phone_number || '',
        website: userData.website || '',
        experience_level: userData.experience_level || 'entry'
      });
      
      // Initialize bio notes from localStorage
      const savedNotes = localStorage.getItem(`bioNotes_${userData.id}`);
      if (savedNotes) {
        setBioNotes(JSON.parse(savedNotes));
      }

      // Set profile data from user object (no need for separate API calls)
      setExperiences(Array.isArray(userData.experiences) ? userData.experiences : []);
      setEducation(Array.isArray(userData.education) ? userData.education : []);
      setSkills(Array.isArray(userData.user_skills) ? userData.user_skills : []);
      
      console.log('📊 Profile data loaded:');
      console.log('- Experiences:', userData.experiences?.length || 0);
      console.log('- Education:', userData.education?.length || 0);
      console.log('- Skills:', userData.user_skills?.length || 0);

      // Fetch user's posts
      const postsData = await feedAPI.getPosts({
        author: profileUserId
      });
      setPosts(postsData.results);

      // Connection status checking will be implemented when backend is ready
    } catch (error) {
      console.error('Error fetching profile data:', error);
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async () => {
    try {
      const updatedUser = await authAPI.updateProfile(editForm);
      setUser(updatedUser);
      
      // Update local profile data if it exists in the updated user
      if (updatedUser.experiences) {
        setExperiences(updatedUser.experiences);
      }
      if (updatedUser.education) {
        setEducation(updatedUser.education);
      }
      if (updatedUser.user_skills) {
        setSkills(updatedUser.user_skills);
      }
      
      setEditingProfile(false);
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  const handleAddBioNote = () => {
    if (newBioNote.trim()) {
      const updatedNotes = [...bioNotes, newBioNote.trim()];
      setBioNotes(updatedNotes);
      // Save to localStorage
      if (currentUser?.id) {
        localStorage.setItem(`bioNotes_${currentUser.id}`, JSON.stringify(updatedNotes));
      }
      setNewBioNote('');
      toast.success('Bio note added');
    }
  };

  const handleRemoveBioNote = (index: number) => {
    const updatedNotes = bioNotes.filter((_, i) => i !== index);
    setBioNotes(updatedNotes);
    // Save to localStorage
    if (currentUser?.id) {
      localStorage.setItem(`bioNotes_${currentUser.id}`, JSON.stringify(updatedNotes));
    }
    toast.success('Bio note removed');
  };

  const handleRemoveSkill = async (skillId: number) => {
    try {
      await usersAPI.removeSkill(skillId);
      setSkills(prevSkills => prevSkills.filter(skill => skill.id !== skillId));
      toast.success('Skill removed successfully');
    } catch (error) {
      toast.error('Failed to remove skill');
    }
  };

  const handleAddSkill = async () => {
    try {
      const newSkill = await usersAPI.addSkill(skillForm.name);
      toast.success('Skill added successfully');
      setAddingSkill(false);
      setSkillForm({ name: '', proficiency: 'intermediate' });
      
      // Update local state instead of refetching all data
      setSkills(prevSkills => [...prevSkills, newSkill]);
    } catch (error) {
      toast.error('Failed to add skill');
    }
  };

  const handleAddExperience = async () => {
    try {
      const newExperience = await usersAPI.addExperience(experienceForm);
      toast.success('Experience added successfully');
      setAddingExperience(false);
      setExperienceForm({
        title: '',
        company: '',
        location: '',
        start_date: '',
        end_date: '',
        is_current: false,
        description: ''
      });
      
      // Update local state instead of refetching all data
      setExperiences(prevExperiences => [...prevExperiences, newExperience]);
    } catch (error) {
      toast.error('Failed to add experience');
    }
  };

  const handleAddEducation = async () => {
    try {
      const educationData = {
        ...educationForm,
        start_year: parseInt(educationForm.start_year) || new Date().getFullYear(),
        end_year: educationForm.end_year ? parseInt(educationForm.end_year) : undefined
      };
      const newEducation = await usersAPI.addEducation(educationData);
      toast.success('Education added successfully');
      setAddingEducation(false);
      setEducationForm({
        school: '',
        degree: '',
        field_of_study: '',
        start_year: '',
        end_year: '',
        description: ''
      });
      
      // Update local state instead of refetching all data
      setEducation(prevEducation => [...prevEducation, newEducation]);
    } catch (error) {
      toast.error('Failed to add education');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long'
    });
  };

  const calculateExperience = () => {
    if (!Array.isArray(experiences) || experiences.length === 0) return 0;
    
    const totalMonths = experiences.reduce((total, exp) => {
      const start = new Date(exp.start_date);
      const end = exp.is_current ? new Date() : new Date(exp.end_date || new Date());
      const months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());
      return total + months;
    }, 0);
    
    return Math.floor(totalMonths / 12);
  };

  const checkConnectionStatus = async () => {
    if (!profileUserId || isOwnProfile) return;
    
    try {
      // Check if already connected or has pending request
      const connections = await connectionsAPI.getConnections();
      const isConnected = connections.results.some(conn => 
        conn.user1.id === profileUserId || conn.user2.id === profileUserId
      );
      
      if (isConnected) {
        setConnectionStatus('connected');
        return;
      }
      
      // Check for pending requests
      const requests = await connectionsAPI.getConnectionRequests();
      const pendingRequest = requests.results.some(req => 
        req.receiver.id === profileUserId && req.status === 'pending'
      );
      
      if (pendingRequest) {
        setConnectionStatus('pending');
      } else {
        setConnectionStatus('none');
      }
    } catch (error) {
      console.error('Error checking connection status:', error);
      // Connections feature not implemented yet
      setConnectionStatus('none');
    }
  };

  const handleConnect = async () => {
    if (!profileUserId || isOwnProfile) return;
    try {
      await connectionsAPI.sendConnectionRequest(profileUserId);
      toast.success('Connection request sent!');
      setConnectionStatus('pending');
    } catch (error) {
      toast.error('Failed to send connection request');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Profile Not Found</h2>
          <p className="text-gray-600 mb-6">The profile you're looking for doesn't exist.</p>
          <Link
            to="/dashboard"
            className="px-6 py-3 bg-green-500 text-white rounded-md hover:bg-green-600"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  // Debug logs removed - data now properly loaded from user object
  

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="space-y-6">
        {/* Profile Header */}
        <div className="bg-white rounded-lg shadow-card overflow-hidden">
          {/* Cover Image */}
          <div className="h-48 bg-gradient-to-r from-linkedin-500 to-linkedin-600 relative">
            {user.cover_image && (
              <img
                src={user.cover_image}
                alt="Cover"
                className="w-full h-full object-cover"
              />
            )}
            {isOwnProfile && (
              <button className="absolute top-4 right-4 p-2 bg-white bg-opacity-80 rounded-full hover:bg-opacity-100 transition-opacity">
                <CameraIcon className="w-5 h-5 text-gray-600" />
              </button>
            )}
          </div>
          
          {/* Profile Info */}
          <div className="p-6">
            <div className="flex items-start space-x-6 -mt-16 mb-6">
              <div className="relative">
                {user.profile_picture ? (
                  <img
                    src={user.profile_picture}
                    alt={`${user.first_name} ${user.last_name}`}
                    className="w-32 h-32 rounded-full border-4 border-white bg-white object-cover"
                  />
                ) : (
                  <div className="w-32 h-32 rounded-full border-4 border-white bg-gray-200 flex items-center justify-center">
                    <UserIcon className="w-16 h-16 text-gray-400" />
                  </div>
                )}
                {isOwnProfile && (
                  <button className="absolute bottom-2 right-2 p-2 bg-white rounded-full shadow-md hover:shadow-lg transition-shadow">
                    <CameraIcon className="w-4 h-4 text-gray-600" />
                  </button>
                )}
              </div>
              
              <div className="flex-1 pt-16">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <h1 className="text-3xl font-bold text-gray-900">
                        {user.first_name} {user.last_name}
                      </h1>
                      <CheckBadgeIcon className="w-6 h-6 text-blue-500" />
                    </div>
                    
                    {user.headline && (
                      <p className="text-lg text-gray-600 mt-1">{user.headline}</p>
                    )}
                    
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                      {user.current_position && (
                        <div className="flex items-center space-x-1">
                          <BriefcaseIcon className="w-4 h-4" />
                          <span>{user.current_position}</span>
                        </div>
                      )}
                      
                      {user.location && (
                        <div className="flex items-center space-x-1">
                          <MapPinIcon className="w-4 h-4" />
                          <span>{user.location}</span>
                        </div>
                      )}
                      
                      {isOwnProfile && calculateExperience() > 0 && (
                        <div className="flex items-center space-x-1">
                          <CalendarIcon className="w-4 h-4" />
                          <span>{calculateExperience()} years experience</span>
                        </div>
                      )}
                      
                      {user.experience_level && (
                        <div className="flex items-center space-x-1">
                          <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium capitalize">
                            {user.experience_level.replace('_', ' ')} Level
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex space-x-3">
                    {isOwnProfile ? (
                      <button
                        onClick={() => setEditingProfile(true)}
                        className="flex items-center space-x-2 px-4 py-2 border border-green-500 text-green-500 rounded-md hover:bg-green-50 transition-colors"
                      >
                        <PencilIcon className="w-4 h-4" />
                        <span>Edit Profile</span>
                      </button>
                    ) : (
                      <>
                        <button 
                          onClick={handleConnect}
                          disabled={connectionStatus !== 'none'}
                          className={`px-4 py-2 rounded-md transition-colors ${
                            connectionStatus === 'connected' 
                              ? 'bg-green-500 text-white cursor-default'
                              : connectionStatus === 'pending'
                              ? 'bg-gray-400 text-white cursor-default'
                              : 'bg-green-500 text-white hover:bg-green-600'
                          }`}
                        >
                          {connectionStatus === 'connected' ? 'Connected' :
                           connectionStatus === 'pending' ? 'Request Sent' : 'Connect'}
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Contact Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
              <div className="flex items-center space-x-2 text-sm">
                <EnvelopeIcon className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">{user.email}</span>
              </div>
              
              {user.phone_number && (
                <div className="flex items-center space-x-2 text-sm">
                  <span className="text-gray-600">{user.phone_number}</span>
                </div>
              )}
              
              {user.website && (
                <div className="flex items-center space-x-2 text-sm">
                  <LinkIcon className="w-4 h-4 text-gray-400" />
                  <a
                    href={user.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-green-600 hover:text-green-700"
                  >
                    Website
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* About Section */}
        {user.about && (
          <div className="bg-white rounded-lg shadow-card p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">About</h2>
            <p className="text-gray-700 whitespace-pre-line">{user.about}</p>
          </div>
        )}

        {/* Bio Notes Section */}
        {isOwnProfile && (
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Personal Notes</h2>
              <button 
                onClick={() => setNewBioNote('')}
                className="p-2 text-gray-400 hover:text-linkedin-600"
              >
                <PlusIcon className="w-5 h-5" />
              </button>
            </div>
            
            {/* Add new bio note */}
            <div className="mb-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newBioNote}
                  onChange={(e) => setNewBioNote(e.target.value)}
                  placeholder="Add a personal note or reminder..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500 text-sm"
                  onKeyPress={(e) => e.key === 'Enter' && handleAddBioNote()}
                />
                <button
                  onClick={handleAddBioNote}
                  disabled={!newBioNote.trim()}
                  className="px-3 py-2 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm"
                >
                  <PlusIcon className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Display bio notes */}
            {bioNotes.length > 0 ? (
              <div className="space-y-2">
                {bioNotes.map((note, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-md">
                    <span className="text-gray-700 text-sm">{note}</span>
                    <button
                      onClick={() => handleRemoveBioNote(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <XMarkIcon className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-3">
                  <TagIcon className="w-6 h-6 text-gray-400" />
                </div>
                <p className="text-gray-500 text-sm">No personal notes added yet</p>
                <p className="text-gray-400 text-xs mt-1">Add notes to remember important details about your profile</p>
              </div>
            )}
          </div>
        )}

        {/* Experience Section */}
        {(experiences.length > 0 || isOwnProfile) && (
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Experience</h2>
              {isOwnProfile && (
                <button 
                  onClick={() => setAddingExperience(true)}
                  className="p-2 text-gray-400 hover:text-linkedin-600"
                >
                  <PlusIcon className="w-5 h-5" />
                </button>
              )}
            </div>
            
            {experiences.length > 0 ? (
              <div className="space-y-6">
                {experiences.map((experience) => (
                  <div key={experience.id} className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center flex-shrink-0">
                      <BuildingOfficeIcon className="w-6 h-6 text-gray-400" />
                    </div>
                    
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{experience.title}</h3>
                      <p className="text-linkedin-600 font-medium">{experience.company}</p>
                      {experience.location && (
                        <p className="text-sm text-gray-600">{experience.location}</p>
                      )}
                      <p className="text-sm text-gray-500 mt-1">
                        {formatDate(experience.start_date)} - {
                          experience.is_current ? 'Present' : formatDate(experience.end_date!)
                        }
                      </p>
                      {experience.description && (
                        <p className="text-gray-700 text-sm mt-2 whitespace-pre-line">
                          {experience.description}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <BriefcaseIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-4">No work experience added yet</p>
                <button
                  onClick={() => setAddingExperience(true)}
                  className="px-4 py-2 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600"
                >
                  Add Your First Experience
                </button>
              </div>
            )}
          </div>
        )}

        {/* Education Section */}
        {(education.length > 0 || isOwnProfile) && (
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Education</h2>
              {isOwnProfile && (
                <button 
                  onClick={() => setAddingEducation(true)}
                  className="p-2 text-gray-400 hover:text-linkedin-600"
                >
                  <PlusIcon className="w-5 h-5" />
                </button>
              )}
            </div>
            
            {education.length > 0 ? (
              <div className="space-y-6">
                {education.map((edu) => (
                  <div key={edu.id} className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center flex-shrink-0">
                      <AcademicCapIcon className="w-6 h-6 text-gray-400" />
                    </div>
                    
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{edu.school}</h3>
                      <p className="text-linkedin-600 font-medium">{edu.degree}</p>
                      {edu.field_of_study && (
                        <p className="text-sm text-gray-600">{edu.field_of_study}</p>
                      )}
                      <p className="text-sm text-gray-500 mt-1">
                        {edu.start_year} - {edu.end_year || 'Present'}
                      </p>
                      {edu.description && (
                        <p className="text-gray-700 text-sm mt-2 whitespace-pre-line">
                          {edu.description}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <AcademicCapIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-4">No education added yet</p>
                <button
                  onClick={() => setAddingEducation(true)}
                  className="px-4 py-2 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600"
                >
                  Add Your First Education
                </button>
              </div>
            )}
          </div>
        )}

        {/* Skills Section */}
        {(skills.length > 0 || isOwnProfile) && (
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Skills</h2>
              {isOwnProfile && (
                <button 
                  onClick={() => setAddingSkill(true)}
                  className="p-2 text-gray-400 hover:text-linkedin-600"
                >
                  <PlusIcon className="w-5 h-5" />
                </button>
              )}
            </div>
            
            {skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {skills.map((userSkill) => (
                  <div
                    key={userSkill.id}
                    className="relative group px-3 py-1 bg-linkedin-100 text-linkedin-700 rounded-full text-sm font-medium"
                  >
                    <span>{userSkill.skill.name}</span>
                    {isOwnProfile && (
                      <button
                        onClick={() => handleRemoveSkill(userSkill.id)}
                        className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                        title="Remove skill"
                      >
                        ×
                      </button>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <TagIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-4">No skills added yet</p>
                <button
                  onClick={() => setAddingSkill(true)}
                  className="px-4 py-2 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600"
                >
                  Add Your First Skill
                </button>
              </div>
            )}
          </div>
        )}

        {/* Recent Activity / Posts */}
        {posts.length > 0 && (
          <div className="bg-white rounded-lg shadow-card p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-4">
              {posts.slice(0, 3).map((post) => (
                <div key={post.id} className="border-b border-gray-100 pb-4 last:border-b-0">
                  <p className="text-gray-700 line-clamp-3">{post.content}</p>
                  <div className="flex items-center justify-between mt-2 text-sm text-gray-500">
                    <span>{formatDate(post.created_at)}</span>
                    <div className="flex items-center space-x-4">
                      <span>{post.likes_count} likes</span>
                      <span>{post.comments_count} comments</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Add Skill Modal */}
      {addingSkill && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Add Skill</h3>
                <button
                  onClick={() => setAddingSkill(false)}
                  className="p-2 text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Skill Name
                  </label>
                  <input
                    type="text"
                    value={skillForm.name}
                    onChange={(e) => setSkillForm({ ...skillForm, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    placeholder="e.g., JavaScript, Project Management"
                  />
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6 pt-6 border-t">
                <button
                  onClick={() => setAddingSkill(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddSkill}
                  disabled={!skillForm.name.trim()}
                  className="flex-1 px-4 py-2 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Add Skill
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Experience Modal */}
      {addingExperience && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Add Experience</h3>
                <button
                  onClick={() => setAddingExperience(false)}
                  className="p-2 text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    value={experienceForm.title}
                    onChange={(e) => setExperienceForm({ ...experienceForm, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company *
                  </label>
                  <input
                    type="text"
                    value={experienceForm.company}
                    onChange={(e) => setExperienceForm({ ...experienceForm, company: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Location
                  </label>
                  <input
                    type="text"
                    value={experienceForm.location}
                    onChange={(e) => setExperienceForm({ ...experienceForm, location: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Start Date *
                    </label>
                    <input
                      type="date"
                      value={experienceForm.start_date}
                      onChange={(e) => setExperienceForm({ ...experienceForm, start_date: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      End Date
                    </label>
                    <input
                      type="date"
                      value={experienceForm.end_date}
                      onChange={(e) => setExperienceForm({ ...experienceForm, end_date: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                      disabled={experienceForm.is_current}
                    />
                  </div>
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_current"
                    checked={experienceForm.is_current}
                    onChange={(e) => setExperienceForm({ 
                      ...experienceForm, 
                      is_current: e.target.checked,
                      end_date: e.target.checked ? '' : experienceForm.end_date
                    })}
                    className="h-4 w-4 text-linkedin-600 focus:ring-linkedin-500 border-gray-300 rounded"
                  />
                  <label htmlFor="is_current" className="ml-2 block text-sm text-gray-900">
                    I currently work here
                  </label>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={experienceForm.description}
                    onChange={(e) => setExperienceForm({ ...experienceForm, description: e.target.value })}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    placeholder="Describe your role and achievements..."
                  />
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6 pt-6 border-t">
                <button
                  onClick={() => setAddingExperience(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddExperience}
                  disabled={!experienceForm.title || !experienceForm.company || !experienceForm.start_date}
                  className="flex-1 px-4 py-2 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Add Experience
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Education Modal */}
      {addingEducation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Add Education</h3>
                <button
                  onClick={() => setAddingEducation(false)}
                  className="p-2 text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    School *
                  </label>
                  <input
                    type="text"
                    value={educationForm.school}
                    onChange={(e) => setEducationForm({ ...educationForm, school: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Degree
                  </label>
                  <input
                    type="text"
                    value={educationForm.degree}
                    onChange={(e) => setEducationForm({ ...educationForm, degree: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    placeholder="e.g., Bachelor of Science"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Field of Study
                  </label>
                  <input
                    type="text"
                    value={educationForm.field_of_study}
                    onChange={(e) => setEducationForm({ ...educationForm, field_of_study: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    placeholder="e.g., Computer Science"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Start Year *
                    </label>
                    <input
                      type="number"
                      value={educationForm.start_year}
                      onChange={(e) => setEducationForm({ ...educationForm, start_year: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                      min="1900"
                      max={new Date().getFullYear()}
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      End Year
                    </label>
                    <input
                      type="number"
                      value={educationForm.end_year}
                      onChange={(e) => setEducationForm({ ...educationForm, end_year: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                      min="1900"
                      max={new Date().getFullYear() + 10}
                      placeholder="Leave empty if ongoing"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={educationForm.description}
                    onChange={(e) => setEducationForm({ ...educationForm, description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    placeholder="Describe your academic achievements, activities, etc."
                  />
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6 pt-6 border-t">
                <button
                  onClick={() => setAddingEducation(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddEducation}
                  disabled={!educationForm.school || !educationForm.start_year}
                  className="flex-1 px-4 py-2 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Add Education
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Profile Modal */}
      {editingProfile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Edit Profile</h3>
                <button
                  onClick={() => setEditingProfile(false)}
                  className="p-2 text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      value={editForm.first_name}
                      onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      value={editForm.last_name}
                      onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Headline
                  </label>
                  <input
                    type="text"
                    value={editForm.headline}
                    onChange={(e) => setEditForm({ ...editForm, headline: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    placeholder="e.g., Software Engineer at Google"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Current Position
                  </label>
                  <input
                    type="text"
                    value={editForm.current_position}
                    onChange={(e) => setEditForm({ ...editForm, current_position: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Location
                    </label>
                    <input
                      type="text"
                      value={editForm.location}
                      onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Industry
                    </label>
                    <input
                      type="text"
                      value={editForm.industry}
                      onChange={(e) => setEditForm({ ...editForm, industry: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    About
                  </label>
                  <textarea
                    value={editForm.about}
                    onChange={(e) => setEditForm({ ...editForm, about: e.target.value })}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    placeholder="Tell us about yourself..."
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={editForm.phone_number}
                      onChange={(e) => setEditForm({ ...editForm, phone_number: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    />
                  </div>
                  
                                  <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Website
                  </label>
                  <input
                    type="url"
                    value={editForm.website}
                    onChange={(e) => setEditForm({ ...editForm, website: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    placeholder="https://..."
                  />
                </div>
              </div>
              
              {/* Experience Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Experience Level
                </label>
                <select
                  value={editForm.experience_level}
                  onChange={(e) => setEditForm({ 
                    ...editForm, 
                    experience_level: e.target.value as 'intern' | 'entry' | 'associate' | 'mid' | 'senior' | 'executive'
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                >
                  <option value="intern">Intern</option>
                  <option value="entry">Entry Level</option>
                  <option value="associate">Associate</option>
                  <option value="mid">Mid Level</option>
                  <option value="senior">Senior</option>
                  <option value="executive">Executive</option>
                </select>
              </div>
              
              {/* Profile Images */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Profile Picture URL
                  </label>
                  <input
                    type="url"
                    value={user?.profile_picture || ''}
                    onChange={(e) => {
                      // This would need to be handled differently for file uploads
                      // For now, showing as read-only URL
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500 bg-gray-50"
                    placeholder="Profile picture URL"
                    readOnly
                  />
                  <p className="text-xs text-gray-500 mt-1">Upload via profile picture button above</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cover Image URL
                  </label>
                  <input
                    type="url"
                    value={user?.cover_image || ''}
                    onChange={(e) => {
                      // This would need to be handled differently for file uploads
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500 bg-gray-50"
                    placeholder="Cover image URL"
                    readOnly
                  />
                  <p className="text-xs text-gray-500 mt-1">Upload via cover image button above</p>
                </div>
              </div>
              
              {/* Additional Info */}
              <div className="pt-4 border-t">
                <h4 className="text-md font-semibold text-gray-900 mb-4">Profile Statistics (Read-only)</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <label className="block text-gray-600">Member Since</label>
                    <p className="font-medium">{new Date(user?.date_joined).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <label className="block text-gray-600">Last Login</label>
                    <p className="font-medium">
                      {user?.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                    </p>
                  </div>
                  <div>
                    <label className="block text-gray-600">Account Type</label>
                    <p className="font-medium">{user?.is_company_user ? 'Company' : 'Individual'}</p>
                  </div>
                  <div>
                    <label className="block text-gray-600">Profile ID</label>
                    <p className="font-medium text-xs text-gray-500">#{user?.id}</p>
                  </div>
                </div>
              </div>
              </div>
              
              <div className="flex space-x-3 mt-6 pt-6 border-t">
                <button
                  onClick={() => setEditingProfile(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateProfile}
                  className="flex-1 px-4 py-2 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage; 