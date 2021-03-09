import {useState,useEffect} from 'react';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
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

const MessageAlert = (props) => {

  useEffect(() => {
    setTimeout(() => {
      props.setMessage(false)
    }, 5000)
  },[])

  return (
    <Alert variant={props.message.variant} dismissible onClose={() => props.setMessage(false)}>
      <Alert.Heading>{props.message.heading}</Alert.Heading>
      <p>{props.message.text}</p>
    </Alert>
  )
}

const Configuration = () => {

  // State variables
  const [show, setShow] = useState(false);
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState(false);
  const [config, setConfig] = useState({
    leds:[],daq:[],port:null,trig:null,stim:[]
  });
  const [ports, setPorts] = useState([]);

  // Close and open COnfiguration
  const handleShow = () => setShow(true);
  const handleHide = () => setShow(false);

  // Send settings to Python
  const handleSave = () => {
    // TODO: Send values to Python API
    fetch('/setup/arduino/set', {
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
    setShow(false);
  };

  const sendMessage = () => {
    setMessage({
      text:"Successfully delivered to Arduino",
      variant:"success",
      heading:"Success:"
    });
  }

  const selectPort = (event) => setConfig({...config, port:event.target.value})

  useEffect(() => {
    fetch('/setup/arduino/list')
      .then( resp => resp.json()
      .then( data => setPorts(data))
    )
    fetch('/setup/arduino/get')
      .then( resp => resp.json()
      .then( data => console.log(data))
    )
  }, []);

  useEffect(() => {
    console.log(config.port);
  },[config.port])

  return(
    <div>
      <Container>
        <Row>
          <Col>

            <Form.Control as="select" custom>
              { ports.length === 0 ?
                <option disabled>No Arduinos Found</option> :
                ports.map((port, idx) => <option onClick={selectPort} key={idx}>{port.device}</option>)}
            </Form.Control>
          </Col>
          <Col>
            <Button variant="primary" onClick={handleShow}>Configure</Button>
          </Col>
        </Row>
        <Row>
          <Col>Arduino</Col>
        </Row>
      </Container>
      <Modal show={show} onHide={handleHide}>
        <Modal.Header closeButton>
          <Modal.Title>Arduino Configuration</Modal.Title>
        </Modal.Header>
        <Button onClick={sendMessage}>Message</Button>
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
          <Button variant="secondary" onClick={handleHide}>
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
        { message ? <MessageAlert setMessage={setMessage} message={message}/> : <Row></Row> }
      </Modal>
    </div>
  )
}

export default function Arduino(){

  return(
    <Configuration/>
  )
}
