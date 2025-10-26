import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { getResumes, findMatchingJobs, getApplications } from '../services/api';

const Dashboard = () => {
  const [resumes, setResumes] = useState([]);
  const [matchingJobs, setMatchingJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch resumes
        const resumesResponse = await getResumes();
        setResumes(resumesResponse.data);
        
        // If there's at least one resume, fetch matching jobs
        if (resumesResponse.data.length > 0) {
          const primaryResume = resumesResponse.data[0];
          const matchingJobsResponse = await findMatchingJobs(primaryResume.id);
          setMatchingJobs(matchingJobsResponse.data);
        }
        
        // Fetch applications
        const applicationsResponse = await getApplications();
        setApplications(applicationsResponse.data);
        
      } catch (err) {
        setError('Failed to load dashboard data. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <Container className="mt-4">
        <Alert variant="info">Loading dashboard data...</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Row className="my-4">
        <Col>
          <h1>Welcome, {user.first_name || user.username}!</h1>
          <p className="lead">Here's your job search overview</p>
        </Col>
      </Row>

      {error && (
        <Row>
          <Col>
            <Alert variant="danger">{error}</Alert>
          </Col>
        </Row>
      )}

      <Row>
        <Col md={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title>Your Resumes</Card.Title>
              {resumes.length === 0 ? (
                <Alert variant="warning">
                  You haven't uploaded any resumes yet.
                  <div className="mt-3">
                    <Link to="/resumes">
                      <Button variant="primary">Upload Resume</Button>
                    </Link>
                  </div>
                </Alert>
              ) : (
                <>
                  <p>You have {resumes.length} resume(s) uploaded.</p>
                  <Link to="/resumes">
                    <Button variant="outline-primary">Manage Resumes</Button>
                  </Link>
                </>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title>Matching Jobs</Card.Title>
              {resumes.length === 0 ? (
                <Alert variant="warning">
                  Upload a resume to see matching jobs.
                </Alert>
              ) : matchingJobs.length === 0 ? (
                <Alert variant="info">
                  No matching jobs found yet. We'll notify you when we find matches.
                </Alert>
              ) : (
                <>
                  <p>We found {matchingJobs.length} jobs matching your profile!</p>
                  <Link to="/jobs">
                    <Button variant="outline-success">View Matching Jobs</Button>
                  </Link>
                </>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title>Your Applications</Card.Title>
              {applications.length === 0 ? (
                <Alert variant="info">
                  You haven't applied to any jobs yet.
                </Alert>
              ) : (
                <>
                  <p>You've applied to {applications.length} job(s).</p>
                  <Link to="/applications">
                    <Button variant="outline-primary">View Applications</Button>
                  </Link>
                </>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mt-4">
        <Col>
          <Card className="shadow-sm">
            <Card.Body>
              <Card.Title>Quick Actions</Card.Title>
              <Row>
                <Col md={3} className="mb-2">
                  <Link to="/jobs">
                    <Button variant="primary" className="w-100">Search Jobs</Button>
                  </Link>
                </Col>
                <Col md={3} className="mb-2">
                  <Link to="/resumes">
                    <Button variant="success" className="w-100">Upload Resume</Button>
                  </Link>
                </Col>
                <Col md={3} className="mb-2">
                  <Link to="/applications">
                    <Button variant="info" className="w-100">Track Applications</Button>
                  </Link>
                </Col>
                <Col md={3} className="mb-2">
                  <Link to="/profile">
                    <Button variant="secondary" className="w-100">Update Profile</Button>
                  </Link>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;