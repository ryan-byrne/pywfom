package previewScreen.views;

import java.awt.EventQueue;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.swing.JFrame;
import javax.swing.UIManager;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;
import javax.swing.JTable;
import java.awt.BorderLayout;
import javax.swing.JLabel;
import javax.swing.JButton;
import java.awt.Font;

import javax.swing.table.AbstractTableModel;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableColumn;
import javax.swing.table.TableModel;
import javax.swing.JTextPane;

public class previewScreen extends JFrame {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private JTable infoTable;
	private JTable cameraTable;

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		try {
			UIManager.setLookAndFeel("com.sun.java.swing.plaf.windows.WindowsLookAndFeel");
		} catch (Throwable e) {
			e.printStackTrace();
		}
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					previewScreen frame = new previewScreen();
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the frame.
	 * @throws JSONException 
	 * @throws FileNotFoundException 
	 */
	public previewScreen() throws FileNotFoundException, JSONException {
		setResizable(false);
		getContentPane().setLayout(null);
		
		JLabel infoLabel = new JLabel("Info:");
		infoLabel.setFont(new Font("Tahoma", Font.BOLD, 13));
		infoLabel.setBounds(10, 11, 46, 14);
		getContentPane().add(infoLabel);
		
		JLabel cameraSettings = new JLabel("Camera Settings:");
		cameraSettings.setFont(new Font("Tahoma", Font.BOLD, 13));
		cameraSettings.setBounds(10, 90, 118, 14);
		getContentPane().add(cameraSettings);
		
		JButton editCamera = new JButton("Edit");
		editCamera.setBounds(150, 144, 89, 23);
		getContentPane().add(editCamera);
		
		JButton editInfo = new JButton("Edit");
		editInfo.setBounds(150, 47, 89, 23);
		getContentPane().add(editInfo);
		JSONObject settings = readJSON("settings");
		final String[] COLUMN_NAMES = {"User", "Mouse", "Timestamp"};
		TableModel infoModel = new AbstractTableModel() {
	          public int getColumnCount() { return 2; }
	          public int getRowCount() { return 3;}
	          public Object getValueAt(int row, int col) { return Integer.valueOf(row*col); }
	    };
		infoTable = new JTable(infoModel);
		infoTable.setEnabled(false);
		infoTable.setModel(null);
		infoTable.setBounds(10, 29, 109, 50);
		getContentPane().add(infoTable);
		cameraTable = new JTable();
		cameraTable.setBounds(10, 115, 109, 95);
		getContentPane().add(cameraTable);
		initComponents();
	}
	private void initComponents() throws FileNotFoundException, JSONException {
		setTitle("Preview Settings");
		
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 330, 262);;
	}


	protected void writeJSON(JSONObject o, String file) throws IOException {
		FileWriter f = new FileWriter(file+".json");
		f.write(o.toString());
		f.flush();
		f.close();
	}

	protected JSONObject readJSON(String file) throws FileNotFoundException, JSONException {
		FileReader r = new FileReader(file+".json");
		JSONTokener t = new JSONTokener(r);
		JSONObject obj = new JSONObject(t);
		return obj;
	}
}
