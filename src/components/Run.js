import Form from 'react-bootstrap/Form';
import Container from 'react-bootstrap/Container';

export default function Run(){
  return (
    <Container>
      <Form>
        <Form.Control type="text" placeholder="Enter UNI" />
        <Form.Control type="text" placeholder="Mouse ID" />
        <Form.Control type="number" placeholder="Run Length" min="0" step="0.01"/>
        <Form.Control type="number" placeholder="Number of Runs" min="0" step="1"/>
        <Form.File/>
      </Form>
    </Container>
  )
}
