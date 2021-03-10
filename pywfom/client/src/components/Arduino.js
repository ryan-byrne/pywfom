import {useState,useEffect} from 'react';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import InputGroup from 'react-bootstrap/InputGroup';
import Modal from 'react-bootstrap/Modal';
import Table from 'react-bootstrap/Table';
import Form from 'react-bootstrap/Form';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Spinner from 'react-bootstrap/Spinner';
import Alert from 'react-bootstrap/Alert';

const StrobingTab = (props) => {

  const addLed = (event) => {
    props.setConfig(
      {...props.config,
        leds:[...props.config.leds, {'name':'New Lew','pin':0}]
      }
    )
  }

  const handleLed = (idx, value, type) => {
    let newLeds = [...props.leds];
    newLeds[idx][type] = value;
    props.setConfig({...props.config, leds:newLeds});
  }

  const handleTrig = (value) => props.setConfig({...props.config, trig:value});

  return (
    <Form>

      <Container>
        <Row></Row>
        <Row>
          <Col></Col>
          <Col>
            <Form.Control type="number" min="0" step="1" placeholder="Trigger Pin"
              onChange={(e)=>handleTrig(e.target.value)}/>
            <Form.Text className="text-muted">
              Set the Trigger Pin
            </Form.Text>
          </Col>
          <Col></Col>
        </Row>

      {props.config.leds.map((led, idx)=>{
        return(
          <Row key={idx}>
            <Col>
              <Form.Control type="text" placeholder="LED Name"
                onChange={(e)=>handleLed(idx, e.target.value, 'name')}/>
            </Col>
            <Col>
              <Form.Control type="number" min="0" step="1" placeholder="LED Pin"
                onChange={(e)=>handleLed(idx, e.target.value, 'pin')}/>
            </Col>
            <Col>
              <Button variant='secondary'>Remove</Button>
            </Col>
            <Col>
              <Button variant='primary'>Test</Button>
            </Col>
          </Row>
        )
      })}

        <Row>
          <Col></Col><Col><Button onClick={addLed}>Add LED</Button></Col><Col></Col>
        </Row>
        <Form.Text className="text-muted">
          Configure LEDs
        </Form.Text>
      </Container>

    </Form>
  )
}

const StimTab = (props) => {

  // TODO: Test Stim
  // TODO: Format Stim
  // TODO: Remove Stim

  const addStim = (event) => {
    props.setConfig(
      {
        ...props.config,
        stim:[...props.config.stim, {'name':'','type':'2PinStepper','pins':["0","1"]}]
      }
    )
  }

  const removeStim = (idx) => {
    let newStim = [...props.config.stim]
    newStim.splice(idx,1)
    props.setConfig({...props.config,stim:newStim})
  }

  const handleStim = (idx, event, type) => {
    let newStim = [...props.config.stim]
    if (type === 'type' && event.target.value !== props.stim[idx].type){
      if (event.target.value==='4PinStepper') {
          newStim[idx].pins.push('0','1');
      } else {
        newStim[idx].pins.splice(-2,2);
      }
    }
    newStim[idx][type] = event.target.value;
    props.setConfig({...props.config, stim:newStim})
  }

  const handlePin = (event, idx, pidx) => {
    let newStim = [...props.config.stim]
    newStim[idx].pins[pidx] = event.target.value
    props.setConfig({...props.config, stim:newStim})

  }

  return (
    <Form>

      <Form.Group as={Row}></Form.Group>

      <Form.Group controlId="stims">
        {props.config.stim.map((stim, idx)=>{
          return(
            <Container>
              <Row key={idx}>
                <Col>
                  <Form.Control type="text" placeholder="Stim Name"
                    onChange={(e)=>handleStim(idx,e,'name')}/>
                </Col>
                <Col>
                  <Form.Control onChange={(e)=>handleStim(idx,e,'type')} as="select">
                    <option>2PinStepper</option>
                    <option>4PinStepper</option>
                  </Form.Control>
                </Col>
                <Col>
                  <Button variant='secondary' onClick={()=>removeStim(idx)}>Remove</Button>
                </Col>
                <Col>
                  <Button variant='primary'>Test</Button>
                </Col>
              </Row>
              {stim.pins.map((pin, pidx) => {
                return (
                  <Row>
                    <Form.Control type="number" min="0" step="1" placeholder="Pin"
                      onChange={(e)=> handlePin(e,idx,pidx)}/>
                  </Row>
                )
              })}
            </Container>
          )
        })}
        </Form.Group>

        <Form.Group>
        <Row>
          <Col></Col><Col><Button onClick={addStim}>Add Stim</Button></Col><Col></Col>
        </Row>
        <Row>
          <Col>
            <Form.Text className="text-muted">
              Configure Stim
            </Form.Text>
          </Col>
        </Row>
        </Form.Group>

    </Form>
  )
}

const DaqTab = (props) => {

  // TODO: Test DAQ
  // TODO: Remove DAQ

  const addDaq = (event) => props.setConfig({...props.config, daq:[{'name':'New DAQ','pin':0}]})

  const removeDaq = (idx) => {
    let newDaq = props.config.daq
    newDaq.splice(idx,1)
    props.setConfig({...props.config,daq:newDaq})
  }

  return (
    <Form>

      <Form.Group as={Row}></Form.Group>

      <Form.Group controlId="stims">
        {props.config.daq.map((daq, idx)=>{
          return(
            <Row key={idx}>
              <Col>
                <Form.Control type="text" placeholder="DAQ Name"/>
              </Col>
              <Col>
                <Form.Control type="number" min="0" step="1" placeholder="DAQ Pin"/>
              </Col>
              <Col>
                <Button onClick={(e)=>removeDaq(idx)} variant='secondary'>Remove</Button>
              </Col>
              <Col>
                <Button variant='primary'>Test</Button>
              </Col>
            </Row>
          )
        })}
      </Form.Group>

      <Form.Group>
        <Row>
          <Col><Button onClick={addDaq}>Add DAQ</Button></Col>
        </Row>
        <Row>
          <Col>
            <Form.Text className="text-muted">
              Configure Data Acquisition
            </Form.Text>
          </Col>
        </Row>
      </Form.Group>

    </Form>
  )
}

const Configuration = (props) => {

  // State variables
  const [sending, setSending] = useState(false);
  const [config, setConfig] = useState({
    "device":"arduino", leds:[],daq:[],port:null,trig:null,stim:[]
  });

  // Send settings to Python
  const handleSave = () => {
    // TODO: Send values to Python API
    fetch('/api/connection/', {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    })
    .then(resp => resp.json()
      .then(data => console.log(data))
      .catch(err => console.log(err))
    )
    props.handleConfig();
  };

  useEffect(() => {
    fetch('/settings/arduino/get')
      .then( resp => resp.json()
      .then( data => console.log(data))
    )
  }, []);

  return(
    <Modal show={props.show} onHide={props.handleConfig}>
      <Modal.Header closeButton>
        <Modal.Title>Arduino Configuration</Modal.Title>
      </Modal.Header>
      <Modal.Body>

        <Tabs>
          <Tab eventKey='strobingTab' title="Strobing">
            <StrobingTab config={config} setConfig={setConfig}/>
          </Tab>
          <Tab eventKey='stimTab' title="Stim">
            <StimTab config={config} setConfig={setConfig}/>
          </Tab>
          <Tab eventKey='daqTab' title="Data Acquisition">
            <DaqTab config={config} setConfig={setConfig}/>
          </Tab>
        </Tabs>

      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={props.handleConfig}>
          Close
        </Button>
        { !sending ?
          <Button variant="primary" onClick={handleSave}>
            Save Changes
          </Button>
          :
          <Button variant="primary" disabled>
            <Spinner as="span" size="sm" animation="border" role="status"/>
            Sending to Arduino
          </Button>
        }
      </Modal.Footer>
    </Modal>
  )
}

export default function Arduino(){

  // Modal View Controllers
  const [config, showConfig] = useState(false);
  const [info, showInfo] = useState(false);
  const [message, setMessage] = useState(null);
  const [disabled, setDisabled] = useState(true);

  // UI State Variables
  const [ports, setPorts] = useState([]);
  const [port, setPort] = useState(0);

  // Close and open Configuration Window
  const handleConfig = () => showConfig(!config);

  const handleInfo = () => showInfo(!info);

  const listPorts = () => {
    fetch('/find/arduinos').then(resp=>resp.json().then(data =>setPorts(data)))
  }

  const connectPort = () => {
    setMessage((
      <Alert variant='warning'>
        <Spinner animation='border' className='mr-3' size='sm'></Spinner>
        Connecting to <b>{ports[port].device}</b>...
      </Alert>
    ))
    fetch('/connect/arduino', {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(ports[port])})
      .then(resp => resp.json()
      .then(data => {
        if (data.status === 'error') {
          setMessage((
            <Alert variant='danger'>
              <p>
                <b>ERROR:</b> Arduino at <b>{ports[port].device}</b> does not have
                compatible firmware.
                <Button className='ml-3'>Upload Firmware...</Button>
              </p>
            </Alert>
          ))
          setDisabled(true);
        }
      }))
  }

  // List available arduinos on Render
  useEffect(() => {
    listPorts();
  }, [])

  useEffect(() => {
    if (ports.length === 0) {}
    else { connectPort() }
  },[ports, port])

  return(
    <Container>
        <Form.Text className='text-muted'>Select an Arduino</Form.Text>
          <InputGroup className="text-center mb-3">
            <Form.Control as="select" custom>
              { ports.length === 0 ?
                <option disabled defaultValue>No Arduinos Found.</option> :
                ports.map((port, idx) => {
                  return(
                    <option onClick={()=>setPort(idx)} key={idx}>
                      {port.product} - {port.device}
                    </option>
                  )
                })
              }
            </Form.Control>
            <ButtonGroup>
              <Button variant="secondary" onClick={()=>listPorts()}>Refresh</Button>
              <Button variant="secondary" onClick={handleInfo}
                disabled={ports.length === 0 ? true : false}>
                { info ? "Hide Info" : "Show Info" }
              </Button>
              <Button variant="primary" disabled={disabled} onClick={handleConfig}>Configure</Button>
            </ButtonGroup>
          </InputGroup>
        <Configuration port={port} show={config} handleConfig={handleConfig}/>
        { message }
        { info ?
            <Table>
              <tbody>
              {Object.keys(ports[port]).map((key,index)=>{
                return (
                  <tr key={index}>
                    <th>{key.charAt(0).toUpperCase()+key.slice(1)}</th>
                    <td>{ports[port][key]}</td>
                  </tr>
                )
              })}
              </tbody>
            </Table>
          : null
        }
      </Container>
  )
}
