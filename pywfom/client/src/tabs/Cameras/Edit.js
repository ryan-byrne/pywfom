import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Alert from 'react-bootstrap/Alert';
import Table from 'react-bootstrap/Table';
import Spinner from 'react-bootstrap/Spinner';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Container from 'react-bootstrap/Container';
import Overlay from 'react-bootstrap/Overlay';
import Tooltip from 'react-bootstrap/Tooltip';

export default function EditCameras(props){

  const [foundCameras, setFoundCameras] = useState([]);
  const [isSearching, setSearching] = useState(false);
  const [showToolTip, setShowToolTip] = useState(false);

  const searchCameras = (event) => {
    setFoundCameras([]);
    setSearching(true);
    fetch('/api/find/cameras')
      .then(resp => resp.json()
      .then(data => {
        setFoundCameras(data);
        setSearching(false);
      }))
  }

  const generateId = (length) => {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
       result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
  }

  const addCamera = (event, idx) => {
    event.target.textContent = 'Adding...';
    event.target.disabled = true;
    const id = generateId(10);
    // Send Message to API
    fetch('/api/configure', {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({command:"open",device:id,config:{...foundCameras[idx],id:id}})})
      .then(resp => resp.json()
      .then(data => {
        if (data.status === 'success'){
          props.setCameras({...props.cameras, [data.config.id]:data.config});
          setFoundCameras(foundCameras.shift(idx))
        } else {
          console.log(data);
        }
      })
    )
  }

  const removeCamera = (event, id) => {
    //Send Message to API
    fetch('/api/configure', {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({command:"close",device:id,config:null})})
    .then(resp => resp.json()
    .then(data => {
      if (data.status === 'success') {
        let cameras = {...props.cameras};
        setFoundCameras([])
        delete cameras[id];
        props.setCameras(cameras)
      } else {
        console.log(data);
      }
    }))
  }

  useEffect(()=> {
    searchCameras(null)
  },[])

  const cameraTable = (cameras, text) => {
    return (
      <Table className="text-center">
        <tbody>
          <th></th><th>Interface</th><th>Index</th><th></th>
          {
          cameras.map((cam, idx)=>{
            const [func, id] = (text == 'Add') ? [addCamera,idx] : [removeCamera,cam.id]
            let add;
            if (text === 'Add') {
              const add = Object.values(props.cameras).map((c)=>{
                if (c.interface === cam.interface && c.index === cam.index) {
                    return false
                } else {
                  return true
                }
              });
              if (!add.every(v=>v===true)) {return null}
            }
            return(
              <tr>
                <td>
                  <Button onClick={(e)=>func(e, id)}>{text}</Button>
                </td>
                <td>{cam.interface}</td>
                <td>{cam.index}</td>
                <td>
                  <Button variant="secondary">Show Info</Button>
                </td>
              </tr>
            )
          })
        }
        </tbody>
      </Table>
    )
  }

  return(
    <div>{
      <Modal show={props.editing} onHide={props.hideEditing}>
        <Modal.Header>
          <Modal.Title>
            Choosing Cameras
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Container>
            <Row className="mb-3">
              <Col>
                <Modal.Title>
                  Available Cameras
                </Modal.Title>
              </Col>
              <Col><Button onClick={searchCameras}>Search</Button></Col>
            </Row>
            <Row className="justify-content-center">
              {
                isSearching ?
                <Alert variant='info'>
                  <Spinner animation="border" size='sm'/>
                    Searching for Cameras...
                </Alert> : null
              }
              {
                foundCameras.length > 0 ? cameraTable(foundCameras, 'Add') : null
              }
            </Row>
            <Row className="mb-3">
              <Col>
                <Modal.Title>
                  Current Cameras
                </Modal.Title>
              </Col>
            </Row>
            <Row className="justify-content-center">
              {
                Object.values(props.cameras).length > 0 ?
                cameraTable(Object.values(props.cameras), 'Remove') :
                <Alert variant='warning'>No Cameras Added</Alert>
              }
            </Row>
          </Container>
        </Modal.Body>
      </Modal>
    }</div>
  )
}
