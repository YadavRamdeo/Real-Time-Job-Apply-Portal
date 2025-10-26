import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Container, Row, Col, Form, Button, Card, Badge, Spinner, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { getJobs, getResumes, findMatchingJobs, searchLiveJobs } from '../services/api';

const JobSearch = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [resumes, setResumes] = useState([]);
  const [useProfile, setUseProfile] = useState(true);
  const [selectedResume, setSelectedResume] = useState('');
  const [minMatch, setMinMatch] = useState(0.6); // 60%
  const [sortBy, setSortBy] = useState('match'); // match | newest | salary
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const [error, setError] = useState('');
  const [selectedSources, setSelectedSources] = useState([]);
  const searchDelay = useRef(null);
  const [searchParams, setSearchParams] = useState({
    search: '',
    location: 'India',
    job_type: '',
    min_salary: ''
  });

  useEffect(() => {
    // Load resumes for profile-based matching
    const init = async () => {
      try {
        const r = await getResumes();
        setResumes(r.data || []);
        if (r.data && r.data.length > 0) {
          setSelectedResume(String(r.data[0].id));
          await fetchJobs({}, true, String(r.data[0].id));
          return;
        }
      } catch (_) {}
      // Fallback to generic search
      await fetchJobs();
    };
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchJobs = async (params = {}, profileMode = useProfile, resumeId = selectedResume) => {
    setLoading(true);
    setError('');
    try {
      if (profileMode && resumeId) {
        const resp = await findMatchingJobs(resumeId, minMatch);
        const list = (resp.data || []).map(item => ({ ...(item.job || {}), match_score: item.match_score }));
        setJobs(list);
      } else {
        // Real-time external search
        const response = await searchLiveJobs({
          q: (searchParams.search || '').trim(),
          location: searchParams.location,
          country: 'India',
          max: 12,
          include_ats: 1,
          ...params
        });
        setJobs(response.data || []);
      }
    } catch (err) {
      console.error('Error fetching jobs:', err);
      setError('Failed to fetch jobs. Please try again.');
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchParams({ ...searchParams, [name]: value });
    // Debounce re-filtering when not using profile API
    if (searchDelay.current) clearTimeout(searchDelay.current);
    searchDelay.current = setTimeout(() => {
      setPage(1);
    }, 300);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setPage(1);
    await fetchJobs();
  };

  const renderJobType = (type) => {
    const variants = {
      'full_time': 'primary',
      'part_time': 'info',
      'contract': 'warning',
      'internship': 'success',
      'remote': 'secondary'
    };
    const labelMap = {
      'full_time': 'full-time',
      'part_time': 'part-time',
    };
    return <Badge bg={variants[type] || 'secondary'}>{labelMap[type] || type}</Badge>;
  };

  // Build source options from jobs
  const sourceOptions = useMemo(() => {
    const s = new Set();
    jobs.forEach(j => { if (j.source) s.add(j.source); });
    return Array.from(s);
  }, [jobs]);

  // Client-side filtering/sorting/pagination for robustness
  const filteredSorted = useMemo(() => {
    let list = [...jobs];
    // Text search
    const q = (searchParams.search || '').toLowerCase();
    if (q) {
      list = list.filter(j => (
        (j.title || '').toLowerCase().includes(q) ||
        (j.company_name || '').toLowerCase().includes(q) ||
        (j.description || '').toLowerCase().includes(q)
      ));
    }
    // Location
    if (searchParams.location) {
      const loc = searchParams.location.toLowerCase();
      list = list.filter(j => (j.location || '').toLowerCase().includes(loc));
    }
    // Type
    if (searchParams.job_type) {
      list = list.filter(j => (j.job_type || '') === searchParams.job_type);
    }
    // Min salary
    if (searchParams.min_salary) {
      const min = Number(searchParams.min_salary) || 0;
      list = list.filter(j => (j.salary_min || 0) >= min);
    }
    // Sources
    if (selectedSources.length > 0) {
      const ss = new Set(selectedSources);
      list = list.filter(j => j.source && ss.has(j.source));
    }
    // Sort
    if (sortBy === 'match') {
      list.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
    } else if (sortBy === 'newest') {
      list.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
    } else if (sortBy === 'salary') {
      list.sort((a, b) => (b.salary_min || 0) - (a.salary_min || 0));
    }
    return list;
  }, [jobs, searchParams, selectedSources, sortBy]);

  const totalPages = Math.max(1, Math.ceil(filteredSorted.length / pageSize));
  const pageClamped = Math.min(page, totalPages);
  const pageItems = useMemo(() =>
    filteredSorted.slice((pageClamped - 1) * pageSize, (pageClamped) * pageSize)
  , [filteredSorted, pageClamped, pageSize]);

  return (
    <Container>
      <h1 className="my-4">Job Search</h1>

      {error && (
        <Alert variant="danger" className="mb-3 d-flex justify-content-between align-items-center">
          <span>{error}</span>
          <Button size="sm" variant="outline-light" onClick={() => fetchJobs()}>Retry</Button>
        </Alert>
      )}
      
      <Card className="mb-4 shadow-sm">
        <Card.Body>
          <Form onSubmit={handleSearch}>
            <Row>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Keywords</Form.Label>
                  <Form.Control
                    type="text"
                    name="search"
                    placeholder="Job title, skills, or company"
                    value={searchParams.search}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Location</Form.Label>
                  <Form.Control
                    type="text"
                    name="location"
                    placeholder="City, state, or remote"
                    value={searchParams.location}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
              <Col md={2}>
                <Form.Group className="mb-3">
                  <Form.Label>Job Type</Form.Label>
                  <Form.Select
                    name="job_type"
                    value={searchParams.job_type}
                    onChange={handleInputChange}
                  >
                    <option value="">All</option>
                    <option value="full_time">Full-time</option>
                    <option value="part_time">Part-time</option>
                    <option value="contract">Contract</option>
                    <option value="internship">Internship</option>
                    <option value="remote">Remote</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={2}>
                <Form.Group className="mb-3">
                  <Form.Label>Min. Salary</Form.Label>
                  <Form.Control
                    type="number"
                    name="min_salary"
                    placeholder="e.g. 800000"
                    value={searchParams.min_salary}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
              <Col md={2}>
                <Form.Group className="mb-3">
                  <Form.Label>Sort By</Form.Label>
                  <Form.Select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                    <option value="match">Best match</option>
                    <option value="newest">Newest</option>
                    <option value="salary">Salary</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Row className="align-items-end">
              <Col md={3}>
                <Form.Check 
                  type="switch" 
                  id="use-profile"
                  label="Use my resume"
                  checked={useProfile}
                  onChange={async (e) => { 
                    setUseProfile(e.target.checked); 
                    setPage(1);
                    await fetchJobs({}, e.target.checked, selectedResume);
                  }}
                />
              </Col>
              <Col md={5}>
                <Form.Group className="mb-3">
                  <Form.Label>Minimum Match: {Math.round(minMatch * 100)}%</Form.Label>
                  <Form.Range 
                    min={0} max={1} step={0.05}
                    value={minMatch}
                    onChange={async (e) => { 
                      const v = Number(e.target.value);
                      setMinMatch(v);
                      setPage(1);
                      if (useProfile && selectedResume) await fetchJobs({}, true, selectedResume);
                    }}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Resume</Form.Label>
                  <Form.Select 
                    value={selectedResume}
                    onChange={async (e) => { 
                      setSelectedResume(e.target.value);
                      setPage(1);
                      if (useProfile) await fetchJobs({}, true, e.target.value);
                    }}
                    disabled={!useProfile}
                  >
                    <option value="">Select a resume</option>
                    {resumes.map(r => <option key={r.id} value={r.id}>{r.title}</option>)}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={8}>
                <Form.Group className="mb-2">
                  <Form.Label>Sources</Form.Label>
                  <Form.Select multiple value={selectedSources} onChange={(e) => {
                    const v = Array.from(e.target.selectedOptions).map(o => o.value);
                    setSelectedSources(v);
                    setPage(1);
                  }}>
                    {sourceOptions.map(src => (
                      <option key={src} value={src}>{src}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4} className="d-flex align-items-end justify-content-end">
                <div className="d-flex gap-2">
                  <Form.Select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }} style={{maxWidth: 120}}>
                    <option value={6}>6 / page</option>
                    <option value={12}>12 / page</option>
                    <option value={24}>24 / page</option>
                  </Form.Select>
                  <Button variant="primary" type="submit" disabled={loading}>
                    {loading ? <><Spinner animation="border" size="sm" /> Searching...</> : 'Search Jobs'}
                  </Button>
                </div>
              </Col>
            </Row>
          </Form>
        </Card.Body>
      </Card>

      {loading ? (
        <div className="text-center my-5">
          <Spinner animation="border" />
          <p className="mt-2">Loading jobs...</p>
        </div>
      ) : jobs.length === 0 ? (
        <Card className="text-center my-5">
          <Card.Body>
            <Card.Title>No jobs found</Card.Title>
            <Card.Text>
              Try adjusting your search criteria or check back later for new job postings.
            </Card.Text>
          </Card.Body>
        </Card>
      ) : (
        <>
        <Row>
          {pageItems.map(item => {
            const job = item.job ? item.job : item;
            const key = job.id || job.application_url;
            return (
              <Col md={6} lg={4} key={key} className="mb-4">
                <Card className="h-100 shadow-sm">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <Card.Title>{job.title}</Card.Title>
                      <div className="d-flex gap-2 align-items-center">
                        {job.source && <Badge bg="dark" className="me-2">{job.source}</Badge>}
                        {renderJobType(job.job_type)}
                      </div>
                    </div>
                    <Card.Subtitle className="mb-2 text-muted">{job.company_name}</Card.Subtitle>
                    <Card.Text className="mb-1">
                      <i className="bi bi-geo-alt"></i> {job.location}
                    </Card.Text>
                    {job.salary_min && (
                      <Card.Text className="mb-2 text-muted">
                        ${job.salary_min.toLocaleString()} - ${job.salary_max ? job.salary_max.toLocaleString() : '?'}
                      </Card.Text>
                    )}
                    <Card.Text className="mb-3">
                      {(job.description || '').substring(0, 100)}...
                    </Card.Text>
                    <div className="d-flex justify-content-between mt-auto">
                      {job.id ? (
                        <Link to={`/jobs/${job.id}`}>
                          <Button variant="outline-primary">View Details</Button>
                        </Link>
                      ) : (
                        <Button variant="outline-primary" href={job.application_url} target="_blank" rel="noreferrer">Open</Button>
                      )}
                      {((item.match_score || job.match_score)) && (
                        <Badge bg="success" className="align-self-center">
                          {Math.round(item.match_score || job.match_score)}% Match
                        </Badge>
                      )}
                    </div>
                  </Card.Body>
                  <Card.Footer className="text-muted">
                    {job.created_at ? <>Posted {new Date(job.created_at).toLocaleDateString()}</> : 'From external source'}
                  </Card.Footer>
                </Card>
              </Col>
            );
          })}
        </Row>
        <div className="d-flex justify-content-between align-items-center my-3">
          <div>
            Page {pageClamped} of {totalPages} — {filteredSorted.length} jobs
          </div>
          <div className="d-flex gap-2">
            <Button variant="outline-secondary" disabled={pageClamped <= 1} onClick={() => setPage(p => Math.max(1, p-1))}>Prev</Button>
            <Button variant="outline-secondary" disabled={pageClamped >= totalPages} onClick={() => setPage(p => Math.min(totalPages, p+1))}>Next</Button>
          </div>
        </div>
        </>
      )}
    </Container>
  );
};

export default JobSearch;
