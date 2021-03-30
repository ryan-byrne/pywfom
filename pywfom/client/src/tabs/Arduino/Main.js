// React Components
import {useState,useEffect, useRef} from 'react';

// Load Components
import Configuration from './Configuration';

// Bootstrap Components
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import InputGroup from 'react-bootstrap/InputGroup';
import Table from 'react-bootstrap/Table';
import Form from 'react-bootstrap/Form';
import Alert from 'react-bootstrap/Alert';
import Spinner from 'react-bootstrap/Spinner';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

export default function Arduino(props){

  // UI State Variables
  const [config, setConfig] = useState({})
  const [availablePorts, setAvailablePorts] = useState([]);
  const [selectedPort, setSelectedPort] = useState(0);
  const [statusMessage, setStatusMessage] = useState(null);

  // Modal View Controllers
  const [configWindow, showConfigWindow] = useState(false);
  const [info, showInfo] = useState(false);

  // Close and open Configuration Window
  const handleConfig = () => showConfigWindow(!configWindow);

  const handleInfo = () => showInfo(!info);

  const listPorts = () => {
    setAvailablePorts([]);
    fetch('/api/devices/arduinos')
      .then(resp=> resp.json()
      .then(data => {
        if (data.length === 0) {
          setStatusMessage(<Alert variant='danger'>No Arduinos Found</Alert>)
        } else {
          setStatusMessage(null);
          setAvailablePorts(data)
        }
      }))
  }

  const connectPort = () => {

    const port = availablePorts[selectedPort];

    setStatusMessage(
      <Alert variant='warning'>
        <Spinner animation='border' className='mr-3' size='sm'></Spinner>
        Connecting to <b>{port.device}</b>...
      </Alert>
    )

    const arduinoSettings = {key:'arduino',port:port.device}

    fetch('/api/settings/arduino', {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(arduinoSettings)})
      .then(resp => resp.json()
      .then(data => {

        if (!data.firmware_version) {

          setStatusMessage((
            <Alert variant='danger'>
              <p>
                <b>ERROR:</b> Arduino at <b>{port.device}</b> does not have
                compatible firmware.
                <Button className='ml-3'>Upload Firmware...</Button>
              </p>
            </Alert>
          ))

        }

        else {

          setConfig(data);
          setStatusMessage((
            <Alert variant='success'>
              <p>
                Connected to the Arduino at <b>{port.device}</b>
              </p>
              <p>Firmware Version: <b>{data.firmware_version}</b></p>
            </Alert>
          ))
        }
      }))
    }

  useEffect(() => {
    if (availablePorts.length === 0) {}
    else { connectPort() }
  },[availablePorts, selectedPort])

  const getConfiguration = () => {
    
  }

  useEffect(() => { listPorts(); getConfiguration()},[])

  return(
    <div>{
      <Container>
        <Row className="mt-3 justify-content-center">
          <Form.Group as={Col} sm={1} lg={4}>
            <Form.Control as="select" custom>
              { availablePorts.length === 0 ?
                <option disabled defaultValue>No Arduinos Found.</option> :
                availablePorts.map((port, idx) => {
                  return(
                    <option onClick={()=>setSelectedPort(idx)} key={idx}>
                      {port.product} - {port.device}
                    </option>
                  )
                })
              }
            </Form.Control>
            <Form.Text muted>Select an Arduino</Form.Text>
          </Form.Group>
          <Form.Group as={Col} sm={4}>
            <ButtonGroup>
              <Button variant="secondary" onClick={()=>listPorts()}>Refresh</Button>
              <Button variant="secondary" onClick={handleInfo}
                disabled={availablePorts.length === 0 ? true : false}>
                { info ? "Hide Info" : "Show Info" }
              </Button>
              <Button variant="primary" disabled={config.firmware_version? false:true }
                onClick={handleConfig}>Configure</Button>
            </ButtonGroup>
          </Form.Group>
        </Row>
        <Row className='justify-content-center'>
          <Col xs={12} md={8}>{statusMessage}</Col>
        </Row>
        <Configuration port={availablePorts[selectedPort]} show={configWindow} handleConfig={handleConfig}/>
      </Container>
    }</div>
  )
}
