package com.example.myapplication;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.view.View;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.InetAddress;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Locale;

public class methodsActivity extends AppCompatActivity {
    private static final int REQUEST_CODE_SPEECH_INPUT =1000;
    public static String localhost="";
    public static int port=0;
    private String cmd = "";
    boolean func1 = false;
    boolean func2 = false;
    boolean func3 = false;
    boolean func4 = false;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTitle("METHODS");
        setContentView(R.layout.activity_methods);
        Toast.makeText(getBaseContext(),localhost+":"+port,Toast.LENGTH_SHORT).show();

    }
    public void returnToPreviousActivity(View view) {
        this.finish();
    }

    public void func1(View view) {
        cmd="#straight";
            if(!func1) {
                Socket_AsyncTask forward = new Socket_AsyncTask();
                forward.execute();
                Toast.makeText(getBaseContext(), "Straight Line Activated", Toast.LENGTH_SHORT).show();
                func1 = true;
            } else{
                Socket_AsyncTask stop = new Socket_AsyncTask();
                stop.execute();
                Toast.makeText(getBaseContext(), "Stopped", Toast.LENGTH_SHORT).show();
                func1 = false;
            }
    }

    public void func2(View view) {
        cmd="#lights";
        if(!func2) {
            Socket_AsyncTask lights = new Socket_AsyncTask();
            lights.execute();
            Toast.makeText(getBaseContext(), "Lights On", Toast.LENGTH_SHORT).show();
            func2 = true;
        } else {
            Socket_AsyncTask lights = new Socket_AsyncTask();
            lights.execute();
            Toast.makeText(getBaseContext(), "Lights Off", Toast.LENGTH_SHORT).show();
            func2 = false;
        }
    }

    public void func3(View view) {
        cmd="#base";
        if(!func3) {
            Socket_AsyncTask right = new Socket_AsyncTask();
            right.execute();
            Toast.makeText(getBaseContext(), "Going Back to Base", Toast.LENGTH_SHORT).show();
            func3 = true;
        } else {
            Socket_AsyncTask stop = new Socket_AsyncTask();
            stop.execute();
            Toast.makeText(getBaseContext(), "Stopped", Toast.LENGTH_SHORT).show();
            func3 = false;
        }
    }

    public void func4(View view) {
        cmd="#park";
        if(!func4) {
            Socket_AsyncTask left = new Socket_AsyncTask();
            left.execute();
            Toast.makeText(getBaseContext(), "Searching for Parking", Toast.LENGTH_SHORT).show();
            func4 = true;
        } else{
            Socket_AsyncTask stop = new Socket_AsyncTask();
            stop.execute();
            Toast.makeText(getBaseContext(), "Stopped", Toast.LENGTH_SHORT).show();
            func4 = false;
        }
    }

    public void Stop(View view) {
        cmd="#stop";
        for(int i =0; i<10; i++) {
            Socket_AsyncTask stop = new Socket_AsyncTask();
                stop.execute();
            }
        Toast.makeText(getBaseContext(),"Stopped",Toast.LENGTH_SHORT).show();
    }

    public void mic(View view) {
        speak();
    }
    private void speak(){
        Intent i = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault());
        i.putExtra(RecognizerIntent.EXTRA_PROMPT,"Command");
        try{
            startActivityForResult(i,REQUEST_CODE_SPEECH_INPUT);
        } catch (Exception e){
            Toast.makeText(this, ""+e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }
    public class Socket_AsyncTask extends AsyncTask<Void,Void,Void>{
            Socket socket;
        @Override
        protected Void doInBackground(Void... voids) {
            try{
                InetAddress inetAddress = InetAddress.getByName(methodsActivity.localhost);
                socket = new java.net.Socket(inetAddress,methodsActivity.port);
                DataOutputStream outputStream=new DataOutputStream(socket.getOutputStream());
                outputStream.writeBytes(cmd);
                outputStream.flush();
                outputStream.close();
                socket.close();
            } catch(IOException e){
                e.printStackTrace();
            }
            return null;
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        switch (requestCode){
            case REQUEST_CODE_SPEECH_INPUT:{
                if(resultCode==RESULT_OK && null!=data){
                    ArrayList<String> str = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
                    callMethod(str.get(0));
                }
            }
        }
    }
    public void callMethod(String str){
        if(str.contains("straight")||str.contains("dark circles")||str.contains("avoid")||str.contains("obstacle")||str.contains("royal")||str.contains("popsicles")||str.contains("aap sickles")||str.contains("circles")||str.contains("asteroids")){
            func1(null);
        } else if(str.contains("light")||str.contains("lite")||str.contains("flight")||str.contains("open")||str.contains("switch")){
            func2(null);
        } else if(str.contains("base")){
            func3(null);
        } else if(str.contains("park")){
            func4(null);
        } else if(str.contains("stop")|| str.contains("top")||str.contains("tab")||str.contains("sab")||str.contains("kab")){
            Stop(null);
        }
    }
}
