import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Alert from 'react-bootstrap/Alert';

export default function Register(props){

  const [registration, setRegistration] = useState({});
  const [configs, setConfigs] = useState([]);
  const [message, setMessage] = useState(null);

  const handleSubmit = () => {
    fetch('/api/auth/register', {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(registration)}).then(resp=>{
        if (resp.ok) { resp.json().then(data=>{props.setConfig(data);props.onHide()}) }
        else {resp.text().then(txt=>setMessage(<Alert variant="danger">{txt}</Alert>))}
      })
  }

  const handleChange = (e) => setRegistration({...registration, [e.target.id]:e.target.value})

  useEffect(()=>{
    fetch('/api/db/configurations').then(resp=>{
      if (resp.ok) { resp.json().then(data=>setConfigs(data)) }
    })
  },[])

  return (
    <div>{
      <Modal show={true} onHide={props.onHide}>
        <Modal.Header>
          <Modal.Title>pyWFOM Registration</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Container>
            <Form.Group as={Row}>
              <Form.Control placeholder="Enter a Username..." id="username" onChange={handleChange}/>
              <Form.Text muted>Username</Form.Text>
            </Form.Group>
            <Form.Group as={Row}>
              <Form.Control placeholder="Enter an Email..." type="email" id="email" onChange={handleChange}/>
              <Form.Text muted>Email</Form.Text>
            </Form.Group>
            <Form.Group as={Row}>
              <Form.Control placeholder="Enter a Password..." type="password" id="password" onChange={handleChange}/>
              <Form.Text muted>Password</Form.Text>
            </Form.Group>
            <Form.Group as={Row}>
              <Form.Control placeholder="Re-Enter the Password..." type="password" id="repassword" onChange={handleChange}/>
              <Form.Text muted>Re-Enter Password</Form.Text>
            </Form.Group>
            <Form.Group>
              <Form.Control as="select" custom id="config" onChange={handleChange}>
                {
                  configs.map((config,idx)=>(
                    <option key={idx}>{config.name}</option>
                  ))
                }
              </Form.Control>
              <Form.Text muted>Select a Default Configuration</Form.Text>
            </Form.Group>
          </Container>
        </Modal.Body>
        {message}
        <Modal.Footer>
          <Button variant="secondary" onClick={(e)=>props.onHide()}>Close</Button>
          <Button onClick={handleSubmit}>Submit</Button>
        </Modal.Footer>
      </Modal>
      }</div>
  )
}
