import sqlite3 from 'sqlite3';

const DB_PATH = 'parking_data.db';

export type ParkingEntry = {
  uuid: string;
  timestamp: string;
  url: string;
  lot_name: string;
  is_full: boolean;
  image_src: string;
};

export async function putParkingData(data: ParkingEntry): Promise<void> {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DB_PATH);
    db.run(
      `INSERT INTO parking_data (uuid, timestamp, lot_name, is_full, url, image_src) VALUES (?, ?, ?, ?, ?, ?)`,
      [data.uuid, data.timestamp, data.lot_name, data.is_full ? 1 : 0, data.url, data.image_src],
      (err) => {
        db.close();
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      }
    );
  });
}

export async function getAllParkingData(): Promise<ParkingEntry[]> {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DB_PATH);
    db.all('SELECT * FROM parkingdata ORDER BY timestamp DESC', (err, rows: any[]) => {
      db.close();
      if (err) {
        reject(err);
      } else {
        resolve(
          rows.map((row) => ({
            uuid: row.uuid,
            timestamp: row.timestamp,
            lot_name: row.lot_name,
            is_full: row.is_full === 1,
            url: row.url,
            image_src: row.image_src,
          }))
        );
      }
    });
  });
}
