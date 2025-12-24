import React, { useState, useEffect } from 'react';
import { Trash2 } from 'lucide-react';
import { api, createTransformedUrl } from '../utils/api';

const Feed = ({ user }) => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchFeed = async () => {
    try {
      const res = await api.get('/feed');
      setPosts(res.data.posts);
    } catch (err) {
      console.error("Failed to load feed", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed();
  }, []);

  const handleDelete = async (postId) => {
    if (!window.confirm("Delete this post?")) return;
    try {
      await api.delete(`/posts/${postId}`);
      setPosts(posts.filter(p => p.id !== postId));
    } catch (err) {
      alert("Failed to delete post");
    }
  };

  if (loading) return <div style={{ textAlign: 'center' }}>Loading feed...</div>;

  return (
    <div>
      <h1 style={{ marginBottom: '30px' }}>🏠 Feed</h1>
      {posts.length === 0 && <p>No posts yet! Be the first to share something.</p>}
      
      {posts.map(post => {
        const isVideo = post.file_type !== 'image';
        // Logic from frontend.py: if image, use caption overlay. If video, use specific resize + caption.
        const mediaUrl = isVideo 
          ? createTransformedUrl(post.url, "w-400,h-200,cm-pad_resize,bg-blurred")
          : createTransformedUrl(post.url, "", post.caption);

        return (
          <div key={post.id} className="post-card">
            <div className="post-header">
              <div>
                <span className="post-user">{post.email}</span>
                <span className="post-date">• {post.created_at.slice(0, 10)}</span>
              </div>
              {post.is_owner && (
                <button className="delete-btn" onClick={() => handleDelete(post.id)}>
                  <Trash2 size={18} />
                </button>
              )}
            </div>
            
            {isVideo ? (
              <>
                <video src={mediaUrl} controls className="post-media" style={{ maxHeight: '400px' }} />
                {post.caption && <div className="post-caption">{post.caption}</div>}
              </>
            ) : (
              <img src={mediaUrl} alt="Post" className="post-media" />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default Feed;