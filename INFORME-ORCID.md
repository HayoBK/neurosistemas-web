# Informe de búsqueda de ORCID iD
Generado por `scripts/buscar_orcid.py` el 4 de agosto de 2026.

Este archivo existe porque **la búsqueda automática no alcanza para decidir**. Se rellenó solo lo inequívoco; el resto necesita que alguien del laboratorio confirme cuál es el perfil correcto.

## Cómo completarlo

1. Revisa los candidatos de cada persona (el enlace abre su perfil ORCID).
2. Marca con una `X` la columna **¿Es?** del que corresponda.
3. Copia ese iD al campo `orcid` de `data/orcid.yaml` — es el que enciende
   la sincronización diaria — y también al de `data/miembros.yaml`, que es
   el que hace aparecer el botón ORCID en su ficha.
4. Si la persona no tiene ORCID, o su perfil está en privado, déjalo vacío:
   la API pública solo devuelve registros públicos y no se rompe nada.

## Estado actual

6 de 12 personas de `data/orcid.yaml` ya tienen su iD.

| Persona | ORCID iD |
|---|---|
| Pedro E. Maldonado | [0000-0001-9895-7684](https://orcid.org/0000-0001-9895-7684) |
| Christ Devia | [0000-0002-2416-0864](https://orcid.org/0000-0002-2416-0864) |
| María de los Ángeles Juricic | [0000-0002-9059-1988](https://orcid.org/0000-0002-9059-1988) |
| José Ignacio Egaña | [0000-0003-1242-0232](https://orcid.org/0000-0003-1242-0232) |
| Iván Plaza | [0000-0002-2112-8439](https://orcid.org/0000-0002-2112-8439) |
| Rocío Loyola | [0000-0001-7637-4277](https://orcid.org/0000-0001-7637-4277) |

### Rellenados en esta corrida

Único candidato con afiliación en la Universidad de Chile.

| Persona | ORCID iD | Afiliaciones declaradas |
|---|---|---|
| José Ignacio Egaña | [0000-0003-1242-0232](https://orcid.org/0000-0003-1242-0232) | Universidad de Chile |

## Pendientes de confirmación

### Cecilia Babul

Sin candidatos con afiliación chilena en la API pública de ORCID. Puede que no tenga perfil, que esté en privado o que no haya declarado afiliación.

### Karla Padilla

| ¿Es? | ORCID iD | Nombre en ORCID | Afiliaciones declaradas |
|:---:|---|---|---|
|  | [0000-0003-0756-7985](https://orcid.org/0000-0003-0756-7985) | Karla Padilla | — |
|  | [0009-0007-3537-1791](https://orcid.org/0009-0007-3537-1791) | KARLA - ISABEL PADILLA | Universidad Nacional de Loja |
|  | [0009-0003-9788-4390](https://orcid.org/0009-0003-9788-4390) | Karla Kristina Padilla | University of California San Diego |
|  | [0000-0001-6173-0750](https://orcid.org/0000-0001-6173-0750) | KARLA HUAMAN PADILLA | — |
|  | [0000-0003-0967-3757](https://orcid.org/0000-0003-0967-3757) | KARLA REA PADILLA | — |

### Samuel Madariaga

| ¿Es? | ORCID iD | Nombre en ORCID | Afiliaciones declaradas |
|:---:|---|---|---|
|  | [0000-0001-6516-5867](https://orcid.org/0000-0001-6516-5867) | Samuel Madariaga Román | — |

### Ismael Jaras

| ¿Es? | ORCID iD | Nombre en ORCID | Afiliaciones declaradas |
|:---:|---|---|---|
|  | [0000-0001-6856-2075](https://orcid.org/0000-0001-6856-2075) | Ismael Jaras | — |

### Carolina Lindsay

| ¿Es? | ORCID iD | Nombre en ORCID | Afiliaciones declaradas |
|:---:|---|---|---|
|  | [0000-0002-2612-7224](https://orcid.org/0000-0002-2612-7224) | Carolina Lindsay Brain | — |
