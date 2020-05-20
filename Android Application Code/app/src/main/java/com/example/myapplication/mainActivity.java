package com.example.myapplication;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;

public class mainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTitle("MAIN MENU");
        setContentView(R.layout.activity_main);
    }

    public void methodsActivity(View view) {
        Intent i = new Intent(this, methodsActivity.class);
        startActivity(i);
    }
    public void connectionActivity(View view){
        Intent i = new Intent(this, connectionsActivity.class);
        startActivity(i);
    }

    public void creditsScreen(View view) {
        Intent i = new Intent(this,creditsActivity.class);
        startActivity(i);
    }
}
