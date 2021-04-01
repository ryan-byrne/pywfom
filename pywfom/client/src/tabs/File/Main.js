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

  const [fileConfig, setFileConfig] = useState(null);

  const closeSession = (event) => {
    fetch('/api/settings', {method:'DELETE'})
      .then(resp => { if (resp.ok) {console.log("Success")} })
  }

  const loadConfiguration = (event) => {
    fetch('/api/file')
      .then(resp => resp.json()
      .then(data => console.log(data)))
  }

  const saveConfiguration = (event) => {}

  const setAsDefault = (event) => {}

  const loadDefault = (event) => {}

  const handleChange = (event) => setFileConfig({...fileConfig, [event.target.id]:event.target.value})

  useEffect(() => {
    fetch('/api/settings/file')
      .then(resp => {
        if (resp.ok) {return resp.json()}
        else { console.error(resp) }})
      .then(data=>setFileConfig(data))
  },[])

  return (
    <div>{
        !fileConfig ? null :
      <Container>
        <Form.Group as={Row} className="mt-3 justify-content-center">{
          [["Enter Username", "user"], ["Enter MouseID", "mouse"]].map(([pl,lbl], idx) => {
            return (
              <Form.Group as={Col} sm={1} md={2} key={idx}>
                <Form.Control placeholder={pl} id={lbl} onChange={handleChange}/>
                <Form.Text muted>{lbl.charAt(0).toUpperCase() + lbl.slice(1)}</Form.Text>
              </Form.Group>
            )
          })
        }</Form.Group>
      {
        <Form.Group as={Row} className="justify-content-center">
          <Form.Group as={Col} xs={4} md={1} className="pr-0">
            <Form.Control type="number" min="0" step="0.01" placeholder="Enter Length of Run"
              id="run_length" value={fileConfig.run_length} onChange={handleChange}/>
            <Form.Text muted>Run Duration</Form.Text>
          </Form.Group>
          <Form.Group as={Col} xs={4} md={1} className="pl-0">
            <Form.Control as="select" value={fileConfig.run_length_unit}
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
              value={fileConfig.number_of_runs}  onChange={handleChange} id="number_of_runs"/>
            <Form.Text muted>Number of Runs</Form.Text>
          </Form.Group>
        </Form.Group>
      }
      <Form.Group as={Row} className="justify-content-center">
        <Col md={4}>
          <Alert variant="success" className="text-center">
            Files to be Saved to: <b>{fileConfig.directory}</b>
          </Alert>
        </Col>
      </Form.Group>
      <Row className="justify-content-center">
          <ButtonGroup>
            <Button variant="danger" className='ml-1' onClick={closeSession}>Close</Button>
            <DropdownButton variant="secondary" className='ml-1' as={ButtonGroup}
              title="File">
              <Dropdown.Item eventKey="1" onClick={saveConfiguration}>Save Configuration</Dropdown.Item>
              <Dropdown.Item eventKey="2" onClick={loadConfiguration}>Load Configuration</Dropdown.Item>
              <Dropdown.Item eventKey="3" onClick={loadDefault}>Load Default</Dropdown.Item>
              <Dropdown.Item eventKey="4" onClick={setAsDefault}>Set As Default</Dropdown.Item>
            </DropdownButton>
            <Button className='ml-1'>Start Acquisition</Button>
          </ButtonGroup>
      </Row>
      </Container>
    }</div>
  )
}
