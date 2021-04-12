import {useEffect, useState} from 'react';

import Form from 'react-bootstrap/Form';
import Alert from 'react-bootstrap/Alert';
import InputGroup from 'react-bootstrap/InputGroup';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Button from 'react-bootstrap/Button';
import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';

export default function File(props){

  const handleChange = (event) => {
    let prevFile = {...props.config.file}
    prevFile[event.target.id] = event.target.value;
    setFile(prevFile);
  }

  const setFile = (data) => props.setConfig({...props.config, file:data})

  return (
    <div>{
      !props.config.file ? null :
      <Container>
        <Form.Group as={Row} className="mt-3 justify-content-center">
            <Form.Group as={Col}>
              <Form.Control value={props.config.username} disabled={true}/>
              <Form.Text muted>
                User <a href="#" onClick={props.close}>Switch</a>
              </Form.Text>
            </Form.Group>
            <Form.Group as={Col}>
              <Form.Control value={props.config.file.mouse}></Form.Control>
              <Form.Text muted>Mouse</Form.Text>
            </Form.Group>
        </Form.Group>
        <Form.Group as={Row} className="justify-content-center">
          <Form.Group as={Col} xs={4} md={1} className="pr-0">
            <Form.Control type="number" min="0" step="0.01" placeholder="Enter Length of Run"
              id="run_length" value={props.config.file.run_length} onChange={handleChange}/>
            <Form.Text muted>Run Duration</Form.Text>
          </Form.Group>
          <Form.Group as={Col} xs={4} md={1} className="pl-0">
            <Form.Control as="select" value={props.config.file.run_length_unit}
              onChange={handleChange} id="run_length_unit" custom>
              {['sec', 'min', 'hr'].map(dur=>{
                return (
                  <option key={dur}>{dur}</option>
                )
              })}
            </Form.Control>
          </Form.Group>
          <Form.Group as={Col} xs={4} md={1} >
            <Form.Control type="number" min="0" step="1" placeholder="Enter Number of Runs"
              value={props.config.file.number_of_runs}  onChange={handleChange} id="number_of_runs"/>
            <Form.Text muted>Number of Runs</Form.Text>
          </Form.Group>
        </Form.Group>
      <Row className="justify-content-center">
          <ButtonGroup>
            <Button variant="danger" className='ml-1' onClick={props.close}>
              Close
            </Button>
            <DropdownButton variant="secondary" className='ml-1' as={ButtonGroup}
              title="Configuration">
              <Dropdown.Item eventKey="0" onClick={props.save}>
                Save
              </Dropdown.Item>
              <Dropdown.Item eventKey="2" onClick={props.load}>
                Load
              </Dropdown.Item>
              <Dropdown.Item eventKey="3" onClick={props.loadDefault}>
                Load Default
              </Dropdown.Item>
              <Dropdown.Item eventKey="4" onClick={props.saveDefault}>
                Save As Default
              </Dropdown.Item>
            </DropdownButton>
            <Button className='ml-1' onClick={props.start}>
              Start Acquisition
            </Button>
          </ButtonGroup>
      </Row>
      </Container>
    }</div>
  )
}
