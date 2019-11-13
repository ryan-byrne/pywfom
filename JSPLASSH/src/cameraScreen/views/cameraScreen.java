package cameraScreen.views;

import java.awt.EventQueue;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JSlider;
import javax.swing.JTextField;
import javax.swing.SwingConstants;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;
import org.json.JSONObject;
import org.json.JSONTokener;

public class cameraScreen extends JFrame {
	
	
	protected static final Object[] String = null;
	private JPanel contentPane;
	List<String> orderList = new ArrayList<String>();
	String orderString = new String();
	int arduinoState = 0;
	int ledState = 0;
	int solisState = 0;
	int mode = 1;
	boolean stimStatus;
	boolean ledOn[] = {false, false, false, false};
	String colors[] = {"Blue","Green","Lime","Red"};
	String mouse = new String();
	String uni = new String();
	boolean readyToDeploy = false;
	private JTextField framerate;
	private JTextField setHeight;
	private JTextField exposureTime;
	private JTextField setWidth;
	private JTextField setBottom;
	private JTextField setTop;

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
					cameraScreen frame = new cameraScreen();
					frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the frame.
	 */
	public cameraScreen() {
		setResizable(false);
		initComponents();
	}
	private void initComponents() {
		setTitle("Camera Settings");
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 330, 254);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		
		JSlider binning = new JSlider();
		binning.setSnapToTicks(true);
		binning.setPaintTicks(true);
		binning.setBounds(15, 45, 43, 111);
		binning.setToolTipText("");
		binning.setOrientation(SwingConstants.VERTICAL);
		binning.setMajorTickSpacing(1);
		binning.setMaximum(4);
		binning.setMinimum(1);
		
		JLabel lblBinning = new JLabel("Binning");
		lblBinning.setBounds(42, 30, 34, 14);
		
		JLabel lblSetFramerate = new JLabel("Set Framerate (fps)");
		lblSetFramerate.setBounds(110, 30, 95, 14);
		lblSetFramerate.setEnabled(false);
		
		framerate = new JTextField();
		framerate.setHorizontalAlignment(SwingConstants.CENTER);
		framerate.setBounds(110, 45, 86, 20);
		framerate.setEnabled(false);
		framerate.setText("50.70");
		framerate.setColumns(10);
		
		JLabel lblSetHeight = new JLabel("Set Height");
		lblSetHeight.setBounds(214, 30, 50, 14);
		
		setHeight = new JTextField();
		setHeight.setHorizontalAlignment(SwingConstants.CENTER);
		setHeight.setBounds(214, 45, 86, 20);
		setHeight.setText("2048");
		setHeight.setColumns(10);
		
		JLabel lblExposureTimes = new JLabel("Exposure Time (s)");
		lblExposureTimes.setBounds(110, 71, 86, 14);
		
		exposureTime = new JTextField();
		exposureTime.setHorizontalAlignment(SwingConstants.CENTER);
		exposureTime.setBounds(110, 91, 86, 20);
		exposureTime.setText("0.0068");
		exposureTime.setColumns(10);
		
		JLabel lblSetWidth = new JLabel("Set Width");
		lblSetWidth.setBounds(214, 71, 47, 14);
		
		setWidth = new JTextField();
		setWidth.setHorizontalAlignment(SwingConstants.CENTER);
		setWidth.setBounds(214, 91, 86, 20);
		setWidth.setText("2048");
		setWidth.setColumns(10);
		
		JLabel lblx = new JLabel("1x1");
		lblx.setBounds(68, 45, 18, 14);
		
		JLabel lblx_1 = new JLabel("2x2");
		lblx_1.setBounds(68, 77, 18, 14);
		
		JLabel lblx_2 = new JLabel("4x4");
		lblx_2.setBounds(68, 110, 18, 14);
		
		JLabel lblx_3 = new JLabel("8x8");
		lblx_3.setBounds(68, 142, 18, 14);
		
		JButton btnDeploySettingsTo_1 = new JButton("Continue");
		btnDeploySettingsTo_1.setEnabled(false);
		btnDeploySettingsTo_1.setBounds(168, 180, 86, 23);
		btnDeploySettingsTo_1.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				int binVal = (int) (16*Math.exp(-0.693*binning.getValue()));
				String b = binVal+"x"+binVal;
				String h = setHeight.getText();
				String w = setWidth.getText();
				String e = exposureTime.getText();
				String f = framerate.getText();
				String btm = setBottom.getText();
				String top = setTop.getText();
				try {
					writeJsonSettings(b, f, h, e, w, btm, top, true);
					System.exit(0);
				} catch (Exception e1) {
					// TODO Auto-generated catch block
					System.out.println(e1.getMessage());
				}
			}

		});
		JLabel lblStrobeOrder = new JLabel();
		lblStrobeOrder.setBounds(264, 235, 0, 0);
		contentPane.setLayout(null);
		contentPane.add(btnDeploySettingsTo_1);
		contentPane.add(lblStrobeOrder);
		contentPane.add(binning);
		contentPane.add(lblx_2);
		contentPane.add(lblx_1);
		contentPane.add(lblx_3);
		contentPane.add(lblx);
		contentPane.add(lblBinning);
		contentPane.add(exposureTime);
		contentPane.add(lblExposureTimes);
		contentPane.add(framerate);
		contentPane.add(lblSetFramerate);
		contentPane.add(setHeight);
		contentPane.add(setWidth);
		contentPane.add(lblSetWidth);
		contentPane.add(lblSetHeight);;
		
		JLabel lblBottom = new JLabel("Bottom");
		lblBottom.setBounds(110, 116, 86, 14);
		contentPane.add(lblBottom);
		
		setBottom = new JTextField();
		setBottom.setHorizontalAlignment(SwingConstants.CENTER);
		setBottom.setText("1");
		setBottom.setColumns(10);
		setBottom.setBounds(110, 136, 86, 20);
		contentPane.add(setBottom);
		
		JLabel lblTop = new JLabel("Top");
		lblTop.setBounds(214, 116, 86, 14);
		contentPane.add(lblTop);
		
		setTop = new JTextField();
		setTop.setHorizontalAlignment(SwingConstants.CENTER);
		setTop.setText("1");
		setTop.setColumns(10);
		setTop.setBounds(214, 136, 86, 20);
		contentPane.add(setTop);
		
		JButton btnPreview = new JButton("Preview");
		btnPreview.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e1) {
				btnDeploySettingsTo_1.setEnabled(true);
				int binVal = (int) (16*Math.exp(-0.693*binning.getValue()));
				String b = binVal+"x"+binVal;
				String h = setHeight.getText();
				String w = setWidth.getText();
				String e = exposureTime.getText();
				String btm = setBottom.getText();
				String top = setTop.getText();
				try {
					Thread.sleep(3000);
					String f_real = readZylaFramerate();
					String e_real = readZylaExpTime();
					framerate.setText(f_real);
					exposureTime.setText(e_real);
					writeJsonSettings(b, f_real, h, e_real, w, btm, top, false);
				} catch (Exception e11) {
					// TODO Auto-generated catch block
					System.out.println(e11.getMessage());
				}
			}
		});
		btnPreview.setBounds(72, 180, 86, 23);
		contentPane.add(btnPreview);
	}


	protected String readZylaExpTime() {
		String path = "../resources/solis_scripts/zyla_settings.txt";
		int count = 0;
		try {
			BufferedReader reader = new BufferedReader(new FileReader(path));
			String line = reader.readLine();
			while (line != null) {
				line = reader.readLine();
				if (count == 4) {
					return line;
				}
				else {
					count++;
				}
			}
			reader.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return null;
	}

	protected String readZylaFramerate() {
		String path = "../resources/solis_scripts/zyla_settings.txt";
		int count = 0;
		try {
			BufferedReader reader = new BufferedReader(new FileReader(path));
			String line = reader.readLine();
			while (line != null) {
				line = reader.readLine();
				if (count == 5) {
					return line;
				}
				else {
					count++;
				}
			}
			reader.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return null;
	}

	private void writeJsonSettings(String b, String f, String h, String e, String w, String btm, String top, Boolean d) throws Exception {
		FileReader reader;
		reader = new FileReader("settings.json");
		JSONTokener tokener = new JSONTokener(reader);
		JSONObject settings = new JSONObject(tokener);
		reader.close();
		JSONObject camera = new JSONObject();
		camera.put("deployed", d);
		camera.put("binning", b);
		camera.put("height", h);
		camera.put("bottom", btm);
		camera.put("width", w);
		camera.put("top", top);
		camera.put("exposure_time", e);
		camera.put("framerate", f);
		settings.put("camera", camera);
		PrintWriter out = new PrintWriter("settings.json");
		out.println(settings.toString());
		out.close();
	}
}
