import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Alert, Spinner, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { getResumes, uploadResume, findMatchingJobs } from '../services/api';

const ResumeManager = () => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [resumeTitle, setResumeTitle] = useState('');
  const [selectedResume, setSelectedResume] = useState(null);
  const [matchingJobs, setMatchingJobs] = useState([]);
  const [loadingMatches, setLoadingMatches] = useState(false);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      setLoading(true);
      const response = await getResumes();
      setResumes(response.data);
    } catch (err) {
      setError('Failed to load resumes. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    // Auto-fill title with filename if empty
    if (!resumeTitle && e.target.files[0]) {
      const fileName = e.target.files[0].name.replace(/\.[^/.]+$/, ""); // Remove extension
      setResumeTitle(fileName);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select a file to upload.');
      return;
    }

    if (!resumeTitle) {
      setError('Please provide a title for your resume.');
      return;
    }

    try {
      setUploading(true);
      setError('');
      setSuccess('');
      
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', resumeTitle);
      
      await uploadResume(formData);
      
      setSuccess('Resume uploaded successfully!');
      setSelectedFile(null);
      setResumeTitle('');
      
      // Refresh resume list
      fetchResumes();
      
    } catch (err) {
      setError(
        err.response?.data?.message || 
        'Failed to upload resume. Please try again.'
      );
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleViewMatches = async (resume) => {
    try {
      setSelectedResume(resume);
      setLoadingMatches(true);
      
      const response = await findMatchingJobs(resume.id);
      setMatchingJobs(response.data);
      
    } catch (err) {
      console.error('Error fetching matching jobs:', err);
    } finally {
      setLoadingMatches(false);
    }
  };

  if (loading) {
    return (
      <Container className="mt-4 text-center">
        <Spinner animation="border" />
        <p>Loading resumes...</p>
      </Container>
    );
  }

  return (
    <Container className="my-4">
      <h1>Resume Manager</h1>
      
      <Row>
        <Col md={6}>
          <Card className="shadow-sm mb-4">
            <Card.Header>
              <h4>Upload New Resume</h4>
            </Card.Header>
            <Card.Body>
              {error && <Alert variant="danger">{error}</Alert>}
              {success && <Alert variant="success">{success}</Alert>}
              
              <Form onSubmit={handleUpload}>
                <Form.Group className="mb-3">
                  <Form.Label>Resume Title</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="e.g., Software Developer Resume"
                    value={resumeTitle}
                    onChange={(e) => setResumeTitle(e.target.value)}
                    required
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Resume File (PDF)</Form.Label>
                  <Form.Control
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileChange}
                    required
                  />
                  <Form.Text className="text-muted">
                    Supported formats: PDF, DOC, DOCX
                  </Form.Text>
                </Form.Group>
                
                <Button 
                  variant="primary" 
                  type="submit" 
                  disabled={uploading || !selectedFile}
                >
                  {uploading ? <><Spinner animation="border" size="sm" /> Uploading...</> : 'Upload Resume'}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card className="shadow-sm mb-4">
            <Card.Header>
              <h4>Your Resumes</h4>
            </Card.Header>
            <Card.Body>
              {resumes.length === 0 ? (
                <Alert variant="info">
                  You haven't uploaded any resumes yet. Upload your first resume to start matching with jobs.
                </Alert>
              ) : (
                <div>
                  {resumes.map(resume => (
                    <Card key={resume.id} className="mb-3">
                      <Card.Body>
                        <div className="d-flex justify-content-between align-items-center">
                          <div>
                            <h5>{resume.title}</h5>
                            <p className="text-muted mb-0">
                              Uploaded: {new Date(resume.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div>
                            <Button 
                              variant="outline-primary" 
                              size="sm" 
                              className="me-2"
                              onClick={() => handleViewMatches(resume)}
                            >
                              View Matching Jobs
                            </Button>
                          </div>
                        </div>
                      </Card.Body>
                    </Card>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
          
          {selectedResume && (
            <Card className="shadow-sm">
              <Card.Header>
                <h4>Matching Jobs for "{selectedResume.title}"</h4>
              </Card.Header>
              <Card.Body>
                {loadingMatches ? (
                  <div className="text-center">
                    <Spinner animation="border" size="sm" />
                    <p>Finding matching jobs...</p>
                  </div>
                ) : matchingJobs.length === 0 ? (
                  <Alert variant="info">
                    No matching jobs found for this resume yet. We'll notify you when we find matches.
                  </Alert>
                ) : (
                  <div>
                    {matchingJobs.map(item => (
                      <Card key={item.job.id} className="mb-2">
                        <Card.Body>
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <h5>{item.job.title}</h5>
                              <p className="text-muted mb-0">{item.job.company_name}</p>
                            </div>
                            <div>
                              <Badge bg="success" className="me-2">
                                {item.match_score}% Match
                              </Badge>
                              {item.job.source && (
                                <Badge bg="dark" className="me-2">{item.job.source}</Badge>
                              )}
                              <Button 
                                variant="outline-primary" 
                                size="sm"
                                as={Link}
                                to={`/jobs/${item.job.id}`}
                              >
                                View Job
                              </Button>
                            </div>
                          </div>
                        </Card.Body>
                      </Card>
                    ))}
                  </div>
                )}
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default ResumeManager;