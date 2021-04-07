import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';

export default function Login() {
  return (
    <div>{
        <Modal show={true}>
          <Modal.Header>
            <Modal.Title>pyWFOM Login</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Container>
              <Form.Group as={Row}>
                <Form.Control placeholder="Username"></Form.Control>
                <Form.Text muted>Username</Form.Text>
              </Form.Group>
              <Form.Group as={Row}>
                <Form.Control placeholder="Password" type="password"></Form.Control>
                <Form.Text muted>Password</Form.Text>
              </Form.Group>
            </Container>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary">Close</Button>
            <Button>Login</Button>
          </Modal.Footer>
        </Modal>
      }</div>
  )
}
