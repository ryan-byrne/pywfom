import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Alert from 'react-bootstrap/Alert';
import Table from 'react-bootstrap/Table';
import Spinner from 'react-bootstrap/Spinner';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Container from 'react-bootstrap/Container';

export default function EditCameras(props){

  const [foundCameras, setFoundCameras] = useState([]);
  const [isSearching, setSearching] = useState(false);

  const searchCameras = (event) => {
    setFoundCameras([]);
    setSearching(true);
    fetch('/api/devices/cameras')
      .then(resp => resp.json()
      .then(data => {
        // Filter out cameras that are already added
        let filteredCameras = data
        Object.values(props.cameras).map(cam=> {
          console.log(cam);
        })
        setFoundCameras(filteredCameras);
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
    fetch('/api/settings/'+id, {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({...foundCameras[idx],id:id}) })
      .then(resp => {
        if (resp.ok) { return resp.json()}
        else { console.error(resp.message) }
      })
      .then(data => {
        let oldCameras = [...foundCameras]
        oldCameras.splice(idx, 1)
        setFoundCameras(oldCameras);
        props.setCameras({...props.cameras, [id]:data})
      })

  }

  const removeCamera = (event, id) => {
    //Send Message to API
    fetch('/api/settings/'+id, {
      method: "DELETE",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({config:null})})
    .then(resp => {
      if (resp.ok) {
        let newCameras = {...props.cameras};
        delete newCameras[id];
        props.setCameras(newCameras)
      }
    })
    .catch(err=> console.log(err))
  }

  useEffect(()=> {
    searchCameras(null)
  },[])
  const cameraTable = (cameras, text) => {
    return (
      <Table className="text-center">
        <tbody>
          <tr><th></th><th>Interface</th><th>Index</th><th></th></tr>
          {
          cameras.map((cam, idx)=>{
            const [func, id] = (text === 'Add') ? [addCamera,idx] : [removeCamera,cam.id]
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
              <tr key={idx}>
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
      <Modal show={props.show} onHide={props.hideEditing}>
        <Modal.Header closeButton>
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
