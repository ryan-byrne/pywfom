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
    let prevFile = {...props.file}
    prevFile[event.target.id] = event.target.value;
    props.setFile(prevFile);
  }

  useEffect(() => {
    fetch('/api/system/file')
      .then(resp => {
        if (resp.ok) {return resp.json()}
        else { console.error(resp) }})
      .then(data=>props.setFile(data))
  },[])

  return (
    <div>{
        !props.file ? null :
      <Container>
        <Form.Group as={Row} className="mt-3 justify-content-center">{
          [["Enter Username", "user"], ["Enter MouseID", "mouse"]].map(([pl,lbl], idx) => {
            return (
              <Form.Group as={Col} sm={1} md={2} key={idx}>
                <Form.Control placeholder={pl} id={lbl} onChange={handleChange}
                  value={props.file[lbl]}/>
                <Form.Text muted>{lbl.charAt(0).toUpperCase() + lbl.slice(1)}</Form.Text>
              </Form.Group>
            )
          })
        }</Form.Group>
      {
        <Form.Group as={Row} className="justify-content-center">
          <Form.Group as={Col} xs={4} md={1} className="pr-0">
            <Form.Control type="number" min="0" step="0.01" placeholder="Enter Length of Run"
              id="run_length" value={props.file.run_length} onChange={handleChange}/>
            <Form.Text muted>Run Duration</Form.Text>
          </Form.Group>
          <Form.Group as={Col} xs={4} md={1} className="pl-0">
            <Form.Control as="select" value={props.file.run_length_unit}
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
              value={props.file.number_of_runs}  onChange={handleChange} id="number_of_runs"/>
            <Form.Text muted>Number of Runs</Form.Text>
          </Form.Group>
        </Form.Group>
      }
      <Form.Group as={Row} className="justify-content-center">
        <Col md={4}>
          <Alert variant="success" className="text-center">
            Files to be Saved to: <b>{props.file.directory}</b>
          </Alert>
        </Col>
      </Form.Group>
      <Row className="justify-content-center">
          <ButtonGroup>
            <Button variant="danger" className='ml-1' onClick={props.handleClose}>
              Close
            </Button>
            <DropdownButton variant="secondary" className='ml-1' as={ButtonGroup}
              title="File">
              <Dropdown.Item eventKey="1" onClick={props.handleSave}>
                Save Configuration
              </Dropdown.Item>
              <Dropdown.Item eventKey="2" onClick={props.handleLoad}>
                Load Configuration
              </Dropdown.Item>
              <Dropdown.Item eventKey="3" onClick={props.handleLoadDefault}>
                Load Default
              </Dropdown.Item>
              <Dropdown.Item eventKey="4" onClick={props.handleSaveDefault}>
                Save As Default
              </Dropdown.Item>
            </DropdownButton>
            <Button className='ml-1' onClick={props.handleStart}>Start Acquisition</Button>
          </ButtonGroup>
      </Row>
      </Container>
    }</div>
  )
}
