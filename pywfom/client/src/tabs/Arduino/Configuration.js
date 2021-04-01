import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Container from 'react-bootstrap/Container';
import Spinner from 'react-bootstrap/Spinner';

const StrobingTab = (props) => {

  const addLed = (event) => {
    props.setConfig({...props.config,
      leds:[...props.config.leds, {name:'New LED',pin:0}]
    })
  }

  const removeLed = (idx) => {
    let newLeds = [...props.config.leds];
    newLeds.splice(idx, 1)
    props.setConfig({...props.config, leds:newLeds})
  }

  const testLed = (idx) => {
    // TODO:
  }

  const handleLed = (event, idx) => {
    const {value, type} = event.target;
    const key = type === 'text' ? 'name' : 'pin';
    let leds = [...props.config.leds];
    leds[idx][key] = value;
    props.setConfig({...props.config, leds:leds})
  }

  return (
    <div>{
      <Container className="mt-3">
        <Form.Group as={Row} className="justify-content-center">
          <Col xs={4} sm={3}>
            <Form.Control type="number" min="0" max="40" step="1" value={props.config.trigger}
              onChange={(e)=>props.setConfig({...props.config, trigger:e.target.value})}/>
            <Form.Text muted>Trigger Pin</Form.Text>
          </Col>
        </Form.Group>
        <Form.Group>
        {
          props.config.leds.map((led, idx) => {
            return (
              <Form.Group key={idx} as={Row} className="justify-content-center">
                <Form.Group as={Col} xs={5}>
                  <Form.Control value={led.name} onChange={(e)=>handleLed(e, idx)}/>
                  <Form.Text muted>LED Name</Form.Text>
                </Form.Group>
                <Form.Group as={Col} xs={4} sm={3}>
                  <Form.Control type="number" min="0" max="40" step="1" value={led.pin}
                    onChange={(e)=>handleLed(e, idx)}/>
                  <Form.Text muted>LED Pin</Form.Text>
                </Form.Group>
                <ButtonGroup as={Col} sm={4} className="h-50">
                  <Button size="sm" variant="secondary" onClick={()=>removeLed(idx)}>Remove</Button>
                  <Button size="sm" onClick={()=>testLed(idx)}>Test</Button>
                </ButtonGroup>
              </Form.Group>
            )
          })
        }
        </Form.Group>
        <Row className="text-center">
          <Col><Button onClick={addLed}>Add LED</Button></Col>
        </Row>
      </Container>
      }</div>
  )
}

const StimTab = (props) => {

  const addStim = (event) => props.setConfig({
    ...props.config, stim:[...props.config.stim, {
      type:'2PinStepper',name:"New Stim",pins:[0,1],stepSize:5
    }]
  })

  const removeStim = (idx) => {
    let newStim = [...props.config.stim];
    newStim.splice(idx, 1)
    props.setConfig({...props.config, stim:newStim})
  }

  const testStim = (idx) => {
    // TODO:
  }

  const handleChange = (event, idx) => {
    const {type, value, id, key} = event.target;
    let newStim = [...props.config.stim]
    if (type === 'select-one'){
      newStim[idx].type = value;
    } else if (type === 'text') {
      newStim[idx].name = value;
    } else if (id.slice(0,3) === 'pin') {
      newStim[idx].pins[parseInt(id.substring(3))] = value;

    } else {
      newStim[idx].stepSize = value
    }
    props.setConfig({...props.config, stim:newStim})
  }

  return (
    <div>{
        <Container className="mt-3">
          {
            props.config.stim.map((s, idx) => {
              return(
                <Form.Group key={idx} as={Row} className="justify-content-center">
                  <Row className="justify-content-center">
                    <Form.Group as={Col} xs={6} sm={5}>
                        <Form.Control value={s.name} onChange={(e)=>handleChange(e, idx)}/>
                        <Form.Text muted>Name</Form.Text>
                      </Form.Group>
                      <Form.Group as={Col} xs={6} sm={5}>
                        <Form.Control as="select" custom value={s.type} onChange={(e)=>handleChange(e, idx)}>
                          <option>2PinStepper</option>
                          <option>4PinStepper</option>
                        </Form.Control>
                        <Form.Text muted>Type</Form.Text>
                      </Form.Group>
                      <Form.Group as={Col} sm={10}>
                        <Row>
                          {
                            [...Array(parseInt(s.type.charAt(0))).keys()].map((pin,pidx)=>{
                              return(
                                <Col key={pidx}>
                                  <Form.Control type="number" id={"pin"+pidx} key={pidx}
                                    value={s.pins[pidx]} onChange={(e)=>handleChange(e,idx)}
                                    min="0" max="40" step="1"/>
                                </Col>
                              )
                            })
                          }
                        </Row>
                        <Form.Text muted>Pins</Form.Text>
                      </Form.Group>
                      <Form.Group as={Col} xs={4} sm={3}>
                        <Form.Control type="number" min="1" step="1" value={s.stepSize}
                          onChange={(e)=>handleChange(e,idx)}/>
                        <Form.Text muted>Step Size</Form.Text>
                      </Form.Group>
                    </Row>
                  <Row>
                    <ButtonGroup as={Col}>
                      <Button size="sm" variant="secondary" onClick={()=>removeStim(idx)}>
                        Remove
                      </Button>
                      <Button size="sm">Test</Button>
                    </ButtonGroup>
                  </Row>
                </Form.Group>
              )
            })
          }
          <Row className="mt-3 text-center">
            <Col><Button onClick={addStim}>Add Stim</Button></Col>
          </Row>
        </Container>
      }</div>
  )
}

const DaqTab = (props) => {

  const handleChange = (event, idx) => {
      let newDaq = [...props.config.daq]
      if (event.target.type==="number") {
        newDaq[idx].pin = event.target.value;
      } else {
        newDaq[idx].name = event.target.value;
      }
      props.setConfig({...props.config, daq:newDaq})
  }

  const addDaq = (event) => props.setConfig({
    ...props.config,daq:[...props.config.daq, {name:'New Daq',pin:0}]
  })

  const removeDaq = (idx) => {
    let newDaq = [...props.config.daq]
    newDaq.splice(idx, 1)
    props.setConfig({...props.config, daq:newDaq})
  }

  const testDaq = (idx) => {
    // TODO:
  }

  return (
    <div>{
        <Container className="mt-3">
          {
            props.config.daq.map((d, idx)=> {
              return(
                <Form.Group as={Row} key={idx} className="justify-content-center">
                  <Form.Group as={Col} xs={5}>
                    <Form.Control value={d.name} onChange={(e)=>handleChange(e,idx)}/>
                    <Form.Text muted>Name</Form.Text>
                  </Form.Group>
                  <Form.Group as={Col} xs={4} sm={3}>
                    <Form.Control value={d.pin} type="number" min="0" max="40"
                      step="1" onChange={(e)=>handleChange(e,idx)}/>
                    <Form.Text muted>Pin</Form.Text>
                  </Form.Group>
                  <ButtonGroup as={Col} className='h-50'>
                    <Button size="sm" variant="secondary" onClick={()=>removeDaq(idx)}>
                      Remove
                    </Button>
                    <Button size="sm">
                      Test
                    </Button>
                  </ButtonGroup>
                </Form.Group>
              )
            })
          }
          <Row className="justify-content-center">
            <Button onClick={addDaq}>Add DAQ</Button>
          </Row>
        </Container>
      }</div>
  )
}

export default function Configuration(props) {

  // State variables
  const [sending, setSending] = useState(false);
  const [config, setConfig] = useState({});

  // Send settings to Python
  const handleConfigure = () => {
    // TODO: Send values to Python API
    fetch('/api/settings/arduino', {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    })
    .then( resp => {
      if (resp.ok) {return resp.json()}
      else { console.error(resp.message)} })
    .then( data =>  setConfig(data))

  };

  useEffect(() => {
    fetch('/api/settings/arduino')
      .then(resp => {
        if (resp.ok) {return resp.json()}
        else { console.error(resp) } } )
      .then( data => setConfig(data) )
  },[])

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
          <Button variant="primary" onClick={handleConfigure}>
            Configure
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
