"""Pre-loaded code samples with intentional issues for demo purposes."""

SAMPLES = {
    "Python — User Service (Multiple Issues)": {
        "language": "Python",
        "code": '''import json, os, sys
import requests

db = {}

def process(d, t):
    # process data
    if t == "create":
        if d["name"] != "" and d["name"] != None:
            db[d["id"]] = d
            x = requests.post("http://api.example.com/users", data=json.dumps(d))
            if x.status_code == 200:
                log = open("log.txt", "a")
                log.write("created " + str(d["id"]))
                return {"status": "ok", "data": d}
            else:
                return {"status": "fail"}
        else:
            return {"status": "fail", "error": "bad name"}
    elif t == "delete":
        del db[d["id"]]
        requests.delete("http://api.example.com/users/" + str(d["id"]))
        log = open("log.txt", "a")
        log.write("deleted " + str(d["id"]))
        return {"status": "ok"}
    elif t == "update":
        db[d["id"]] = d
        requests.put("http://api.example.com/users/" + str(d["id"]), data=json.dumps(d))
        log = open("log.txt", "a")
        log.write("updated " + str(d["id"]))
        return {"status": "ok", "data": d}
    elif t == "get":
        return {"status": "ok", "data": db[d["id"]]}
    else:
        return {"status": "fail"}
''',
    },
    "JavaScript — API Handler (Callback Hell)": {
        "language": "JavaScript",
        "code": '''function getUserData(userId, callback) {
  fetch("/api/users/" + userId)
    .then(function(response) {
      response.json().then(function(user) {
        fetch("/api/orders/" + user.id)
          .then(function(response2) {
            response2.json().then(function(orders) {
              fetch("/api/payments/" + orders[0].id)
                .then(function(response3) {
                  response3.json().then(function(payment) {
                    var result = {};
                    result.user = user;
                    result.orders = orders;
                    result.payment = payment;
                    result.total = 0;
                    for (var i = 0; i < orders.length; i++) {
                      result.total = result.total + orders[i].amount;
                    }
                    callback(null, result);
                  })
                })
                .catch(function(err) { callback(err); })
            })
          })
          .catch(function(err) { callback(err); })
      })
    })
    .catch(function(err) { callback(err); })
}

function validateEmail(email) {
  if (email.indexOf("@") > -1) {
    return true;
  }
  return false;
}

function formatPrice(p) {
  return "$" + p;
}
''',
    },
    "Java — Order Processor (SOLID Violations)": {
        "language": "Java",
        "code": '''public class OrderProcessor {
    public String processOrder(Map<String, Object> order) {
        // Validate
        if (order.get("items") == null) return "ERROR";
        if (order.get("customer") == null) return "ERROR";
        if (((List)order.get("items")).size() == 0) return "ERROR";

        // Calculate total
        double total = 0;
        List<Map<String, Object>> items = (List<Map<String, Object>>) order.get("items");
        for (int i = 0; i < items.size(); i++) {
            double price = (Double) items.get(i).get("price");
            int qty = (Integer) items.get(i).get("qty");
            if ((String)items.get(i).get("category") == "electronics") {
                total += price * qty * 1.15; // 15% tax
            } else if ((String)items.get(i).get("category") == "food") {
                total += price * qty * 1.05; // 5% tax
            } else {
                total += price * qty * 1.10; // 10% tax
            }
        }

        // Apply discount
        if (total > 100) total = total * 0.9;
        if (total > 500) total = total * 0.85;

        // Send email
        try {
            Properties props = new Properties();
            props.put("mail.smtp.host", "smtp.gmail.com");
            props.put("mail.smtp.port", "587");
            Session session = Session.getInstance(props);
            MimeMessage msg = new MimeMessage(session);
            msg.setSubject("Order Confirmation");
            msg.setText("Your total is $" + total);
            msg.setRecipients(Message.RecipientType.TO,
                InternetAddress.parse((String)order.get("email")));
            Transport.send(msg);
        } catch (Exception e) {
            System.out.println("Email failed");
        }

        // Save to DB
        try {
            Connection conn = DriverManager.getConnection(
                "jdbc:mysql://localhost:3306/orders", "root", "password123");
            PreparedStatement ps = conn.prepareStatement(
                "INSERT INTO orders VALUES (?, ?, ?)");
            ps.setString(1, (String) order.get("id"));
            ps.setDouble(2, total);
            ps.setString(3, new SimpleDateFormat("yyyy-MM-dd").format(new Date()));
            ps.executeUpdate();
        } catch (Exception e) {
            System.out.println("DB failed");
        }

        return "OK:" + total;
    }
}
''',
    },
    "Go — HTTP Handler (Error Handling Issues)": {
        "language": "Go",
        "code": '''package main

import (
\t"database/sql"
\t"encoding/json"
\t"fmt"
\t"net/http"
)

var db *sql.DB

type User struct {
\tId       int
\tname     string
\tEmail    string
\tpassword string
}

func handleUsers(w http.ResponseWriter, r *http.Request) {
\tif r.Method == "GET" {
\t\trows, _ := db.Query("SELECT * FROM users WHERE id = " + r.URL.Query().Get("id"))
\t\tvar users []User
\t\tfor rows.Next() {
\t\t\tvar u User
\t\t\trows.Scan(&u.Id, &u.name, &u.Email, &u.password)
\t\t\tusers = append(users, u)
\t\t}
\t\tjson.NewEncoder(w).Encode(users)
\t} else if r.Method == "POST" {
\t\tvar u User
\t\tjson.NewDecoder(r.Body).Decode(&u)
\t\tdb.Exec(fmt.Sprintf("INSERT INTO users VALUES (%d, '%s', '%s', '%s')",
\t\t\tu.Id, u.name, u.Email, u.password))
\t\tw.Write([]byte("ok"))
\t} else if r.Method == "DELETE" {
\t\tid := r.URL.Query().Get("id")
\t\tdb.Exec("DELETE FROM users WHERE id = " + id)
\t\tw.Write([]byte("deleted"))
\t}
}

func main() {
\tdb, _ = sql.Open("mysql", "root:pass@/mydb")
\thttp.HandleFunc("/users", handleUsers)
\tfmt.Println("Server starting...")
\thttp.ListenAndServe(":8080", nil)
}
''',
    },
}
