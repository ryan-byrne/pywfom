// React Components
import {useState,useEffect} from 'react';

// Load Components
import Configuration from './Configuration';

// Bootstrap Components
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import InputGroup from 'react-bootstrap/InputGroup';
import Modal from 'react-bootstrap/Modal';
import Table from 'react-bootstrap/Table';
import Form from 'react-bootstrap/Form';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import Alert from 'react-bootstrap/Alert';
import Spinner from 'react-bootstrap/Spinner';
import Container from 'react-bootstrap/Container';

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
    fetch('/api/find/arduinos')
      .then(resp=> resp.json()
      .then(data => setPorts(data)
      ))
  }

  const connectPort = () => {
    setMessage((
      <Alert variant='warning'>
        <Spinner animation='border' className='mr-3' size='sm'></Spinner>
        Connecting to <b>{ports[port].device}</b>...
      </Alert>
    ))
    fetch('/api/connection/arduino', {
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
        } else {
          setMessage((
            <Alert variant='success'>
              <p>
                Successfully connected to the Arduino at <b>{ports[port].device}</b>
              </p>
            </Alert>
          ))
        }
      }))
  }

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
