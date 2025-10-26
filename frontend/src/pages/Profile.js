import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { getUserProfile, updateUserProfile } from '../services/api';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    location: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: ''
  });

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      const response = await getUserProfile();
      setProfile(response.data);
      
      // Initialize form with user data
      const { user, ...profileData } = response.data;
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: profileData.phone || '',
        location: profileData.location || '',
        linkedin_url: profileData.linkedin_url || '',
        github_url: profileData.github_url || '',
        portfolio_url: profileData.portfolio_url || ''
      });
      
    } catch (err) {
      setError('Failed to load profile. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      await updateUserProfile({
        user: {
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email
        },
        phone: formData.phone,
        location: formData.location,
        linkedin_url: formData.linkedin_url,
        github_url: formData.github_url,
        portfolio_url: formData.portfolio_url
      });
      
      setSuccess('Profile updated successfully!');
      
      // Update local storage user data
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      localStorage.setItem('user', JSON.stringify({
        ...user,
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email
      }));
      
    } catch (err) {
      setError(
        err.response?.data?.message || 
        'Failed to update profile. Please try again.'
      );
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Container className="mt-4 text-center">
        <Spinner animation="border" />
        <p>Loading profile...</p>
      </Container>
    );
  }

  return (
    <Container className="my-4">
      <h1>Your Profile</h1>
      
      <Card className="shadow-sm">
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>First Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                  />
                </Form.Group>
              </Col>
              
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Last Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </Form.Group>
              </Col>
              
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Phone</Form.Label>
                  <Form.Control
                    type="text"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Form.Group className="mb-3">
              <Form.Label>Location</Form.Label>
              <Form.Control
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="City, State, Country"
              />
            </Form.Group>
            
            <h4 className="mt-4">Social Profiles</h4>
            
            <Form.Group className="mb-3">
              <Form.Label>LinkedIn URL</Form.Label>
              <Form.Control
                type="url"
                name="linkedin_url"
                value={formData.linkedin_url}
                onChange={handleChange}
                placeholder="https://linkedin.com/in/yourprofile"
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>GitHub URL</Form.Label>
              <Form.Control
                type="url"
                name="github_url"
                value={formData.github_url}
                onChange={handleChange}
                placeholder="https://github.com/yourusername"
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Portfolio URL</Form.Label>
              <Form.Control
                type="url"
                name="portfolio_url"
                value={formData.portfolio_url}
                onChange={handleChange}
                placeholder="https://yourportfolio.com"
              />
            </Form.Group>
            
            <div className="d-grid gap-2 mt-4">
              <Button 
                variant="primary" 
                type="submit" 
                disabled={saving}
              >
                {saving ? <><Spinner animation="border" size="sm" /> Saving...</> : 'Save Changes'}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Profile;