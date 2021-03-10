import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import Container from 'react-bootstrap/Container';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Button from 'react-bootstrap/Button';


export default function File(){
  return (
    <Container>
      <InputGroup className="m-3">
        <Form.Control type="text" placeholder="Enter UNI" />
        <Form.Control className="ml-3" type="text" placeholder="Mouse ID" />
      </InputGroup>
      <InputGroup className="m-3">
        <Form.Control type="number" placeholder="Run Length" min="0" step="0.01"/>
        <Form.Control className="mr-5" as="select">
          <option>Sec</option>
          <option>Min</option>
          <option>Hr</option>
        </Form.Control>
        <Form.Control className="ml-3" type="number" placeholder="Number of Runs" min="0" step="1"/>
      </InputGroup>
      <InputGroup className="m-3">
        <Form.File/>
      </InputGroup>
      <ButtonGroup className="float-right">
        <Button variant="secondary">Close</Button>
        <Button variant="secondary" className='ml-1 mr-1'>Set Default</Button>
        <Button>Start Acquisition</Button>
      </ButtonGroup>

    </Container>
  )
}
