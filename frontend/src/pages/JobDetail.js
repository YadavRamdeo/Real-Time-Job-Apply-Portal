import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Badge, Alert, Form, Modal, Spinner } from 'react-bootstrap';
import { useParams, useNavigate } from 'react-router-dom';
import { getJobById, getResumes, applyToJob } from '../services/api';

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [selectedResume, setSelectedResume] = useState('');
  const [coverLetter, setCoverLetter] = useState('');
  const [applying, setApplying] = useState(false);
  const [applyError, setApplyError] = useState('');

  useEffect(() => {
    const fetchJobAndResumes = async () => {
      try {
        setLoading(true);
        
        // Fetch job details
        const jobResponse = await getJobById(id);
        setJob(jobResponse.data);
        
        // Fetch user's resumes
        const resumesResponse = await getResumes();
        setResumes(resumesResponse.data);
        
        if (resumesResponse.data.length > 0) {
          setSelectedResume(resumesResponse.data[0].id);
        }
        
      } catch (err) {
        setError('Failed to load job details. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobAndResumes();
  }, [id]);

  const handleApply = async () => {
    if (!selectedResume) {
      setApplyError('Please select a resume to apply with.');
      return;
    }

    try {
      setApplying(true);
      setApplyError('');
      
      await applyToJob(job.id, selectedResume, coverLetter);
      
      // Close modal and navigate to applications page
      setShowApplyModal(false);
      navigate('/applications', { state: { message: 'Application submitted successfully!' } });
      
    } catch (err) {
      setApplyError(
        err.response?.data?.message || 
        'Failed to submit application. Please try again.'
      );
      console.error(err);
    } finally {
      setApplying(false);
    }
  };

  if (loading) {
    return (
      <Container className="mt-4 text-center">
        <Spinner animation="border" />
        <p>Loading job details...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">{error}</Alert>
        <Button variant="primary" onClick={() => navigate(-1)}>Go Back</Button>
      </Container>
    );
  }

  if (!job) {
    return (
      <Container className="mt-4">
        <Alert variant="warning">Job not found.</Alert>
        <Button variant="primary" onClick={() => navigate('/jobs')}>Back to Jobs</Button>
      </Container>
    );
  }

  return (
    <Container className="my-4">
      <Button variant="outline-secondary" className="mb-3" onClick={() => navigate(-1)}>
        &larr; Back to Jobs
      </Button>
      
      <Card className="shadow-sm mb-4">
        <Card.Body>
          <Row>
            <Col md={8}>
              <h1>{job.title}</h1>
              <h5 className="text-muted">{job.company_name}</h5>
              <div className="mb-3">
                <Badge bg="secondary" className="me-2">{job.location}</Badge>
                <Badge bg="primary">{job.job_type}</Badge>{' '}
                {job.source && <Badge bg="dark">{job.source}</Badge>}
                {job.match_score && (
                  <Badge bg="success" className="ms-2">{job.match_score}% Match</Badge>
                )}
              </div>
              {job.salary_min && (
                <p className="text-muted">
                  Salary: ${job.salary_min.toLocaleString()} 
                  {job.salary_max ? ` - $${job.salary_max.toLocaleString()}` : ''}
                </p>
              )}
            </Col>
            <Col md={4} className="text-md-end">
              <Button 
                variant="success" 
                size="lg" 
                className="mt-2"
                onClick={() => setShowApplyModal(true)}
                disabled={resumes.length === 0}
              >
                Apply Now
              </Button>
              {resumes.length === 0 && (
                <div className="mt-2 text-danger">
                  <small>You need to upload a resume first</small>
                </div>
              )}
            </Col>
          </Row>
        </Card.Body>
      </Card>
      
      <Row>
        <Col md={8}>
          <Card className="shadow-sm mb-4">
            <Card.Header>
              <h4>Job Description</h4>
            </Card.Header>
            <Card.Body>
              <div dangerouslySetInnerHTML={{ __html: job.description }} />
            </Card.Body>
          </Card>
          
          <Card className="shadow-sm mb-4">
            <Card.Header>
              <h4>Requirements</h4>
            </Card.Header>
            <Card.Body>
              <div dangerouslySetInnerHTML={{ __html: job.requirements }} />
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4}>
          <Card className="shadow-sm mb-4">
            <Card.Header>
              <h4>Company</h4>
            </Card.Header>
            <Card.Body>
              <h5>{job.company_name}</h5>
              {job.application_url && (
                <Button 
                  variant="outline-primary" 
                  href={job.application_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  Apply at Source
                </Button>
              )}
            </Card.Body>
          </Card>
          
          <Card className="shadow-sm">
            <Card.Header>
              <h4>Job Details</h4>
            </Card.Header>
            <Card.Body>
              <p><strong>Posted:</strong> {new Date(job.created_at).toLocaleDateString()}</p>
              <p><strong>Location:</strong> {job.location}</p>
              <p><strong>Job Type:</strong> {job.job_type}</p>
              {job.salary_min && (
                <p>
                  <strong>Salary Range:</strong> ${job.salary_min.toLocaleString()} 
                  {job.salary_max ? ` - $${job.salary_max.toLocaleString()}` : ''}
                </p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Apply Modal */}
      <Modal show={showApplyModal} onHide={() => setShowApplyModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Apply for {job.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {applyError && <Alert variant="danger">{applyError}</Alert>}
          
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Select Resume</Form.Label>
              <Form.Select 
                value={selectedResume} 
                onChange={(e) => setSelectedResume(e.target.value)}
                required
              >
                <option value="">Select a resume</option>
                {resumes.map(resume => (
                  <option key={resume.id} value={resume.id}>
                    {resume.title}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Cover Letter (Optional)</Form.Label>
              <Form.Control 
                as="textarea" 
                rows={6} 
                value={coverLetter}
                onChange={(e) => setCoverLetter(e.target.value)}
                placeholder="Introduce yourself and explain why you're a good fit for this position..."
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowApplyModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="success" 
            onClick={handleApply}
            disabled={applying || !selectedResume}
          >
            {applying ? <><Spinner animation="border" size="sm" /> Submitting...</> : 'Submit Application'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default JobDetail;