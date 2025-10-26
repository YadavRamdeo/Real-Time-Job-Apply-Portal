import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Badge, Button, Form, Spinner } from 'react-bootstrap';
import { useLocation } from 'react-router-dom';
import { getApplications, updateApplicationStatus } from '../services/api';

const Applications = () => {
  const location = useLocation();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState(location.state?.message || '');

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      const response = await getApplications();
      setApplications(response.data);
    } catch (err) {
      setError('Failed to load applications. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (applicationId, newStatus) => {
    try {
      await updateApplicationStatus(applicationId, newStatus);
      
      // Update local state
      setApplications(applications.map(app => 
        app.id === applicationId ? { ...app, status: newStatus } : app
      ));
      
      setMessage('Application status updated successfully!');
      
      // Clear message after 3 seconds
      setTimeout(() => setMessage(''), 3000);
      
    } catch (err) {
      setError('Failed to update application status. Please try again.');
      console.error(err);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      'applied': 'primary',
      'reviewing': 'info',
      'interview': 'warning',
      'offered': 'success',
      'rejected': 'danger',
      'accepted': 'success',
      'declined': 'secondary'
    };
    
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  if (loading) {
    return (
      <Container className="mt-4 text-center">
        <Spinner animation="border" />
        <p>Loading your applications...</p>
      </Container>
    );
  }

  return (
    <Container className="my-4">
      <h1>Your Job Applications</h1>
      
      {message && (
        <div className="alert alert-success">{message}</div>
      )}
      
      {error && (
        <div className="alert alert-danger">{error}</div>
      )}
      
      {applications.length === 0 ? (
        <Card className="text-center my-5">
          <Card.Body>
            <Card.Title>No applications found</Card.Title>
            <Card.Text>
              You haven't applied to any jobs yet. Start searching for jobs to apply!
            </Card.Text>
            <Button variant="primary" href="/jobs">Search Jobs</Button>
          </Card.Body>
        </Card>
      ) : (
        <Row>
          {applications.map(application => (
            <Col md={6} key={application.id} className="mb-4">
              <Card className="h-100 shadow-sm">
                <Card.Header className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">{application.job_title}</h5>
                  {getStatusBadge(application.status)}
                </Card.Header>
                <Card.Body>
                  <Card.Subtitle className="mb-2 text-muted">
                    {application.company_name}
                  </Card.Subtitle>
                  <p><strong>Applied:</strong> {new Date(application.applied_date).toLocaleDateString()}</p>
                  <p><strong>Resume:</strong> {application.resume_title}</p>
                  <p><strong>Match Score:</strong> {application.match_score}%</p>
                  
                  {application.cover_letter && (
                    <div className="mb-3">
                      <strong>Cover Letter:</strong>
                      <p className="text-muted">{application.cover_letter}</p>
                    </div>
                  )}
                  
                  <div className="mt-3">
                    <Form.Group>
                      <Form.Label><strong>Update Status:</strong></Form.Label>
                      <Form.Select 
                        value={application.status}
                        onChange={(e) => handleStatusChange(application.id, e.target.value)}
                      >
                        <option value="applied">Applied</option>
                        <option value="reviewing">Under Review</option>
                        <option value="interview">Interview Scheduled</option>
                        <option value="offered">Job Offered</option>
                        <option value="rejected">Rejected</option>
                        <option value="accepted">Accepted Offer</option>
                        <option value="declined">Declined Offer</option>
                      </Form.Select>
                    </Form.Group>
                  </div>
                  
                  {application.notes && (
                    <div className="mt-3">
                      <strong>Notes:</strong>
                      <p>{application.notes}</p>
                    </div>
                  )}
                </Card.Body>
                <Card.Footer>
                  <Button 
                    variant="outline-primary" 
                    href={`/jobs/${application.job.id}`}
                    className="w-100"
                  >
                    View Job Details
                  </Button>
                </Card.Footer>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </Container>
  );
};

export default Applications;