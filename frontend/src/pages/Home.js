import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <Container>
      <Row className="my-5">
        <Col md={12} className="text-center">
          <h1>Welcome to Job Portal</h1>
          <p className="lead">
            Find your dream job with our AI-powered job matching system
          </p>
        </Col>
      </Row>
      
      <Row className="my-5">
        <Col md={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title>Smart Job Matching</Card.Title>
              <Card.Text>
                Our AI analyzes your resume and matches you with the perfect job opportunities.
              </Card.Text>
              <Link to="/register">
                <Button variant="primary">Get Started</Button>
              </Link>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title>Real-time Updates</Card.Title>
              <Card.Text>
                Receive instant notifications when new matching jobs are available.
              </Card.Text>
              <Link to="/register">
                <Button variant="primary">Sign Up Now</Button>
              </Link>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title>Automated Applications</Card.Title>
              <Card.Text>
                Apply to multiple jobs with a single click using your saved resume.
              </Card.Text>
              <Link to="/register">
                <Button variant="primary">Join Today</Button>
              </Link>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Row className="my-5">
        <Col md={12} className="text-center">
          <h2>How It Works</h2>
          <p>
            Upload your resume, set your job preferences, and let our AI do the rest.
            We'll scan company career pages and job boards to find the best matches for you.
          </p>
          <Link to="/register">
            <Button variant="success" size="lg" className="mt-3">
              Create Your Account
            </Button>
          </Link>
        </Col>
      </Row>
    </Container>
  );
};

export default Home;