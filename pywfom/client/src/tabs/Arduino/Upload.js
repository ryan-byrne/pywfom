import {useEffect, useState} from 'react';
import Modal from 'react-bootstrap/Modal';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Table from 'react-bootstrap/Table';
import Form from 'react-bootstrap/Form';

export default function Upload(props){

  const [boardType, setBoardType] = useState("Uno");
  const [versions, setVersions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [message, setMessage] = useState(null);

  const uploadFirmware = () => {}

  const retrieveFirmware = () => {
    setMessage(
      <Alert variant="info">
        Loading Available Firmware Versions...
      </Alert>
    )
    setVersions([]);
    fetch('https://api.github.com/repos/ryan-byrne/pywfom/contents/firmware/versions').then(resp=>{
      resp.json().then(data=>{
        setVersions(data);
        setMessage(
          <Alert variant="warning">
            <b>Warning: </b>Uploading will erase the firmware currently on the Arduino
          </Alert>
        )
      })
    })
  }

  useEffect(()=>retrieveFirmware(),[])

  return (
    <div>{
        <Modal show={props.uploading} onHide={()=>props.setUploading(false)}>
          <Modal.Header closeButton>
            <Modal.Title>Upload pyWFOM Firmware to Arduino:</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Table striped bordered hover size="sm">
              <tbody>
                <tr><th>Available Firmware Versions:</th></tr>
                {
                  versions.map((version, idx)=>{
                    const style = {
                      cursor: "pointer",
                      color:idx===selected?"red":"gray"
                    }
                    return (
                      <tr><td onClick={()=>setSelected(idx)} style={style}>{version.name}</td></tr>
                    )
                  })
                }
              </tbody>
            </Table>
            <Form.Group>
              <Form.Control as="select" custom value={boardType} onChange={(e)=>setBoardType(e.target.value)}>
                {['Uno', 'Mega'].map(type=><option>{type}</option>)}
              </Form.Control>
              <Form.Text muted>Select the Board Type</Form.Text>
            </Form.Group>
            {message}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={()=>props.setUploading(false)}>Cancel</Button>
            <Button onClick={()=>uploadFirmware()}>Upload</Button>
          </Modal.Footer>
        </Modal>
      }</div>
  )
}
