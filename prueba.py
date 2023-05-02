import pandas as pd

def municipios():
        municipios = pd.read_csv(r"C:\Users\Julian\Documents\booking_scraper\municipios.csv")
        df = pd.DataFrame(municipios)
        Lista = {col: df[col].dropna().tolist() for col in df.columns}
        return Lista

def main():
    Lista = municipios()
    print(Lista["Nombre Municipio"][0])

if __name__ == "__main__":
    main()